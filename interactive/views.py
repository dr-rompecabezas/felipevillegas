"""AI chat proxy for the InteractivePage.

The chat is single-turn by design: the client posts one user message, the view
forwards it to Anthropic with a two-part system prompt and returns the reply.
There is no conversation history stored or replayed.

System prompt assembly:
    - The page's `chat_system_prompt` (Wagtail-editable) supplies style and
      scope rules — how the bot talks, what's out of bounds.
    - `interactive/data/profile.md` (version-controlled) supplies the factual
      source of truth about Felipe — career, projects, skills, scope notes.
    - The two are concatenated and sent as a single cache-marked system block
      so Anthropic can serve them from the prompt cache on subsequent calls.

Cost and abuse controls are layered, all keyed by client IP:
    1. Hard input length cap (cheap rejection before any model call).
    2. Per-IP requests-per-minute throttle (atomic per-minute bucket).
    3. Per-IP daily input + output token budgets (atomic counters). With
       prompt caching enabled, `usage.input_tokens` excludes cache reads,
       so the input budget effectively measures the user's message portion
       and not the (cached) system prompt.
    4. `max_tokens` clamped to remaining output budget so a single response
       cannot overshoot the daily cap.

Standard Django CSRF applies — the client must send X-CSRFToken.
"""

import json
import logging
import time
from datetime import timedelta
from pathlib import Path

import anthropic
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from interactive.models import InteractivePage

logger = logging.getLogger(__name__)

PROFILE_PATH = Path(__file__).resolve().parent / "data" / "profile.md"


def _load_profile_text() -> str:
    """Read profile.md once at import time. Missing file is non-fatal —
    the chat falls back to just the editable system prompt."""
    try:
        return PROFILE_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        logger.warning("profile.md not found at %s — chat will run without it.", PROFILE_PATH)
        return ""


_PROFILE_TEXT = _load_profile_text()


def _build_system_prompt(page_prompt: str) -> str:
    """Combine the editable page prompt (style/scope frame) with the
    version-controlled profile (factual context). Page prompt comes first
    so its style and scope rules anchor the model before it sees the facts.
    """
    parts = [p.strip() for p in (page_prompt, _PROFILE_TEXT) if p and p.strip()]
    return "\n\n---\n\n".join(parts)


def _client_ip(request: HttpRequest) -> str:
    """Resolve the client IP for rate-limit and budget keys.

    With `CHAT_TRUSTED_PROXY_COUNT=N`, take the Nth-from-the-right value of
    X-Forwarded-For. Anything to the left is client-supplied and untrusted, so
    a forged leftmost entry cannot be used to spoof past the trusted hops.
    Falls back to REMOTE_ADDR when XFF is missing or has fewer entries than
    the trusted count.
    """
    trusted = max(getattr(settings, "CHAT_TRUSTED_PROXY_COUNT", 1), 0)
    xff = request.headers.get("x-forwarded-for", "")
    if xff and trusted > 0:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if len(parts) >= trusted:
            return parts[-trusted]
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _today_key() -> str:
    return timezone.now().strftime("%Y-%m-%d")


def _seconds_until_midnight() -> int:
    now = timezone.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return max(int((midnight - now).total_seconds()), 60)


def _rpm_check(ip: str) -> bool:
    """Atomic per-minute fixed-bucket RPM check. Returns True if allowed."""
    bucket = int(time.time() // 60)
    key = f"chat:rpm:{ip}:{bucket}"
    cache.add(key, 0, timeout=90)
    new_count = cache.incr(key)
    return new_count <= settings.CHAT_RPM


def _budget_remaining(ip: str) -> tuple[int, int]:
    """Return (input_remaining, output_remaining) for today."""
    day = _today_key()
    used_in = cache.get(f"chat:in:{ip}:{day}") or 0
    used_out = cache.get(f"chat:out:{ip}:{day}") or 0
    return (
        max(settings.CHAT_DAILY_INPUT_TOKEN_BUDGET - used_in, 0),
        max(settings.CHAT_DAILY_OUTPUT_TOKEN_BUDGET - used_out, 0),
    )


def _record_usage(ip: str, input_tokens: int, output_tokens: int) -> None:
    """Atomically record token usage so concurrent requests do not undercount."""
    day = _today_key()
    ttl = _seconds_until_midnight()
    in_key = f"chat:in:{ip}:{day}"
    out_key = f"chat:out:{ip}:{day}"
    cache.add(in_key, 0, timeout=ttl)
    cache.add(out_key, 0, timeout=ttl)
    if input_tokens:
        cache.incr(in_key, input_tokens)
    if output_tokens:
        cache.incr(out_key, output_tokens)


def _err(code: str, message: str, status: int, **extra) -> JsonResponse:
    payload = {"error": code, "message": message, **extra}
    return JsonResponse(payload, status=status)


@require_POST
def chat(request: HttpRequest) -> JsonResponse:
    page = InteractivePage.objects.live().first()
    if page is None or not page.chat_enabled:
        return _err("disabled", "Chat is not available.", 404)

    if not settings.ANTHROPIC_API_KEY:
        logger.warning("Chat request received but ANTHROPIC_API_KEY is not set.")
        return _err("disabled", "Chat is not configured.", 503)

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _err("bad_request", "Invalid JSON body.", 400)

    user_message = (body.get("message") or "").strip()
    if not user_message:
        return _err("bad_request", "Message is required.", 400)

    if len(user_message) > settings.CHAT_INPUT_MAX_CHARS:
        return _err(
            "input_too_long",
            f"Messages are capped at {settings.CHAT_INPUT_MAX_CHARS} characters.",
            413,
            limit=settings.CHAT_INPUT_MAX_CHARS,
        )

    ip = _client_ip(request)

    if not _rpm_check(ip):
        return _err(
            "rate_limited",
            "Too many requests. Please slow down and try again in a moment.",
            429,
            retry_after=60,
        )

    input_remaining, output_remaining = _budget_remaining(ip)
    if input_remaining <= 0 or output_remaining <= 0:
        return _err(
            "budget_exhausted",
            "Daily chat budget reached. Email f.villegas@thinkelearn.com to continue the conversation.",
            429,
            contact_email="f.villegas@thinkelearn.com",
        )

    system_prompt = _build_system_prompt(page.chat_system_prompt or "")
    # Mark the combined system prompt as cacheable. The prompt is identical
    # on every call (page prompt rarely changes; profile.md is loaded once),
    # so Anthropic serves it from cache after the first request and only
    # bills the user message portion on subsequent calls.
    system_blocks = (
        [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]
        if system_prompt
        else []
    )
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Cap max_tokens to what's left of today's output budget so a single
    # response cannot overshoot the daily cap. Anthropic requires >= 1.
    max_tokens = max(min(settings.CHAT_MAX_OUTPUT_TOKENS, output_remaining), 1)

    try:
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system_blocks,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIError as exc:
        logger.exception("Anthropic API error: %s", exc)
        return _err(
            "upstream_error",
            "The chat service is temporarily unavailable. Email f.villegas@thinkelearn.com.",
            502,
            contact_email="f.villegas@thinkelearn.com",
        )

    reply = "".join(getattr(block, "text", "") for block in response.content).strip()
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    _record_usage(ip, input_tokens, output_tokens)

    return JsonResponse(
        {
            "reply": reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    )
