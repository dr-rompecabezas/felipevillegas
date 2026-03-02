# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All Python commands use `uv run`. There is no `activate` step.

```bash
# Development server
uv run python manage.py runserver

# Migrations
uv run python manage.py makemigrations <app>   # always name the app explicitly
uv run python manage.py migrate

# Tests
uv run python manage.py test                   # all tests
uv run python manage.py test home.tests        # single app
uv run python manage.py test home.tests.TestHomePage.test_context  # single test

# System check
uv run python manage.py check

# First-time setup
uv run python manage.py create_initial_pages   # builds page tree + sets Site root
uv run python manage.py createsuperuser
```

The `.env` file is loaded automatically via `python-decouple`. Minimum required keys: `SECRET_KEY`. See `.env.example` for all variables.

## Architecture

This is a **Wagtail CMS** site. Page content is managed entirely through the Wagtail admin at `/cms/`. There are no custom URL routes — page URLs are defined by the Wagtail page tree.

### Settings split

`config/settings/` has three files:

- `base.py` — shared config; all secrets read via `decouple.config()`
- `dev.py` — SQLite fallback (no `DATABASE_URL` needed), debug toolbar enabled
- `production.py` — S3 media via `django-storages`, WhiteNoise static files, security headers, Stripe keys

`DJANGO_SETTINGS_MODULE` defaults to `config.settings.dev` in `manage.py` and `wsgi.py`.

### Page model hierarchy

```text
wagtailcore.Page (root)
└── home.HomePage           ← site root page
    ├── work.WorkIndexPage
    │   └── work.ProjectPage (many)
    ├── photography.PhotographyIndexPage
    │   └── photography.GalleryPage (many)
    └── contact.ContactPage
```

`parent_page_types` and `subpage_types` enforce this structure in the admin.

### Key model notes

**`HomePage`** (`home/models.py`) — content is a single `StreamField` with five block types: `HeroBlock`, `AboutBlock`, `FeaturedWorkBlock`, `SkillsBlock`, `ContactCTABlock`. `get_context()` injects `featured_projects` (up to 6 `ProjectPage` objects with `featured=True`) for the `FeaturedWorkBlock` to render.

**`ProjectPage`** (`work/models.py`) — the most data-rich model. `tech_stack` is a `ParentalManyToManyField` to the `TechTag` snippet (managed in the Wagtail snippets UI). `primary_domain` drives the filter on `WorkIndexPage` via `?domain=ld|software|hybrid`.

**`GalleryPage`** (`photography/models.py`) — `images` is a `StreamField` of `ImageChooserBlock`s; the template renders them as a CSS masonry grid.

**`ContactPage`** (`contact/models.py`) — no model fields; all contact content (email, LinkedIn, ThinkElearn) is hardcoded in the template.

### Templates & CSS

- Global shell: `templates/base.html` — includes Tailwind via CDN for development.
- App templates live in `<app>/templates/<app>/<model_snake>.html` (Wagtail convention).
- For production, build CSS with: `npm run build` (Tailwind CLI, outputs to `staticfiles/css/output.css`).
- `ImageChooserPanel` was removed in Wagtail 6+. Use `FieldPanel` for all image `ForeignKey` fields.

### Deployment

Railway is configured via `railway.json`: gunicorn starts the WSGI server; `python manage.py migrate` runs as a release command before each deploy. Static files are collected and served by WhiteNoise; media files go to S3.
