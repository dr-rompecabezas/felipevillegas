"""AI chat proxy for the InteractivePage.

The chat is single-turn by design: the client posts one user message, the view
forwards it to Anthropic with the page's `chat_system_prompt`, and returns the
reply. There is no conversation history stored or replayed.

Cost and abuse controls are layered, all keyed by client IP:
    1. Hard input length cap (cheap rejection before any model call).
    2. Per-IP requests-per-minute throttle (sliding window via cache).
    3. Per-IP daily input + output token budgets (cumulative via cache).

Standard Django CSRF applies — the client must send X-CSRFToken.
"""

import json
import logging
import time
from datetime import timedelta

import anthropic
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from interactive.models import InteractivePage

logger = logging.getLogger(__name__)


def _client_ip(request: HttpRequest) -> str:
    """Best-effort client IP for rate-limit and budget keys.

    Trusts the leftmost X-Forwarded-For value when present (Railway sets it),
    falling back to REMOTE_ADDR otherwise.
    """
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _today_key() -> str:
    return timezone.now().strftime("%Y-%m-%d")


def _seconds_until_midnight() -> int:
    now = timezone.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return max(int((midnight - now).total_seconds()), 60)


def _rpm_check(ip: str) -> bool:
    """Sliding-window RPM check. Returns True if the request is allowed."""
    key = f"chat:rpm:{ip}"
    now = time.time()
    window_start = now - 60
    timestamps = cache.get(key) or []
    timestamps = [t for t in timestamps if t > window_start]
    if len(timestamps) >= settings.CHAT_RPM:
        return False
    timestamps.append(now)
    cache.set(key, timestamps, timeout=120)
    return True


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
    day = _today_key()
    ttl = _seconds_until_midnight()
    in_key = f"chat:in:{ip}:{day}"
    out_key = f"chat:out:{ip}:{day}"
    cache.set(in_key, (cache.get(in_key) or 0) + input_tokens, timeout=ttl)
    cache.set(out_key, (cache.get(out_key) or 0) + output_tokens, timeout=ttl)


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

    system_prompt = page.chat_system_prompt or ""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.CHAT_MAX_OUTPUT_TOKENS,
            system=system_prompt,
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
