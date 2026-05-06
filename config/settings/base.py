from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=lambda v: [s.strip() for s in v.split(",")])

INSTALLED_APPS = [
    "users",
    "core",
    "home",
    "work",
    "photography",
    "contact",
    "interactive",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django_htmx",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English")]
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

AUTH_USER_MODEL = "users.User"

WAGTAIL_SITE_NAME = "Felipe Villegas"
WAGTAILADMIN_BASE_URL = config("WAGTAILADMIN_BASE_URL", default="http://localhost:8000")

WAGTAILIMAGES_IMAGE_MODEL = "wagtailimages.Image"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Interactive page chat (Anthropic) ─────────────────────────────────
# All limits read from env so production can tune without a code deploy.
# The Anthropic console hard monthly cap is the last line of defence and
# must be set manually — see README.
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL = config("ANTHROPIC_MODEL", default="claude-haiku-4-5-20251001")
CHAT_DAILY_INPUT_TOKEN_BUDGET = config("CHAT_DAILY_INPUT_TOKEN_BUDGET", default=5000, cast=int)
CHAT_DAILY_OUTPUT_TOKEN_BUDGET = config("CHAT_DAILY_OUTPUT_TOKEN_BUDGET", default=2000, cast=int)
CHAT_RPM = config("CHAT_RPM", default=6, cast=int)
CHAT_INPUT_MAX_CHARS = config("CHAT_INPUT_MAX_CHARS", default=1000, cast=int)
CHAT_MAX_OUTPUT_TOKENS = config("CHAT_MAX_OUTPUT_TOKENS", default=400, cast=int)
# How many trusted proxies sit in front of Django. The chat view picks the
# Nth-from-the-right entry in X-Forwarded-For so a client cannot spoof their
# IP past the trusted hop count. Railway = 1.
CHAT_TRUSTED_PROXY_COUNT = config("CHAT_TRUSTED_PROXY_COUNT", default=1, cast=int)
