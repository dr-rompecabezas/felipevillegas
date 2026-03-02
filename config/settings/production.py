import os

import dj_database_url
from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

# ── Sentry ───────────────────────────────────────────────────────────
if os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from django.core.exceptions import DisallowedHost
    from sentry_sdk.integrations.django import DjangoIntegration

    def _sentry_before_send(event, hint):
        """Drop noisy scanner traffic using wildcard Host headers."""
        exc_info = hint.get("exc_info")
        if not exc_info:
            return event
        exc_type, _, _ = exc_info
        if exc_type and issubclass(exc_type, DisallowedHost):
            request = event.get("request") or {}
            host = request.get("headers", {}).get("Host") or request.get("headers", {}).get("X-Forwarded-Host") or ""
            if "*" in host:
                return None
        return event

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.2,
        send_default_pii=True,
        before_send=_sentry_before_send,
    )

# ── Hosts & origins ─────────────────────────────────────────────────
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "ALLOWED_HOSTS",
        "felipevillegas.com,www.felipevillegas.com",
    ).split(",")
    if h.strip()
]
# Auto-include Railway-provided domains so health checks work.
for _railway_var in ("RAILWAY_PUBLIC_DOMAIN", "RAILWAY_PRIVATE_DOMAIN"):
    _railway_host = os.environ.get(_railway_var)
    if _railway_host and _railway_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_railway_host)

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

# ── Database ─────────────────────────────────────────────────────────
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── S3 media storage ────────────────────────────────────────────────
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="ca-central-1")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# ── Storage backends (Django 4.2+) ──────────────────────────────────
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ── WhiteNoise ───────────────────────────────────────────────────────
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

# ── Security ─────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Logging ──────────────────────────────────────────────────────────
_LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": _LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _LOG_LEVEL,
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
