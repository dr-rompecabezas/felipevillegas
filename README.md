# felipevillegas.com

Personal professional portfolio site for Felipe Villegas — L&D practitioner and software engineer.

Built with Django 6.0 + Wagtail 7.3. Content is managed through the Wagtail admin; there are no hardcoded page routes.

## Local setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/dr-rompecabezas/felipevillegas.git
cd felipevillegas

cp .env.example .env
# edit .env — at minimum set SECRET_KEY

uv sync
uv run python manage.py migrate
uv run python manage.py create_initial_pages
uv run python manage.py populate_home_page
uv run python manage.py populate_projects
uv run python manage.py populate_seo
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

- Site: <http://localhost:8000>
- Wagtail admin: <http://localhost:8000/admin/>

Dev uses SQLite by default. Set `DATABASE_URL` in `.env` to use PostgreSQL instead.

## Page tree

`create_initial_pages` builds the full tree and points the default Site at `HomePage`:

```text
Root
└── HomePage                 → /
    ├── WorkIndexPage        → /work/
    ├── PhotographyIndexPage → /photography/
    └── ContactPage          → /contact/
```

## Content seeding

Four management commands populate launch content after the page tree exists:

| Command | What it does |
| --- | --- |
| `populate_home_page` | Seeds the `HomePage` StreamField (hero, about, skills, contact CTA) |
| `populate_projects` | Creates all `TechTag` snippets and `ProjectPage` entries under `WorkIndexPage` |
| `populate_seo` | Sets `seo_title` and `search_description` on the four static/index pages |

All three are idempotent and accept `--force` to overwrite existing content. `ProjectPage` and `GalleryPage` can also be added and edited through the Wagtail admin at `/admin/`.

## Environment variables

See `.env.example` for the full list. Production-only variables (S3) can be left blank in development.

| Variable | Required | Notes |
| --- | --- | --- |
| `SECRET_KEY` | Always | Any long random string in dev |
| `DATABASE_URL` | Production | Defaults to SQLite in dev |
| `AWS_*` | Production | S3 media storage |
| `WAGTAILADMIN_BASE_URL` | Production | Used in Wagtail email links |

## Deployment

Deployed on Railway. Push to `main` triggers an auto-deploy:

1. `python manage.py migrate` (release command)
2. `gunicorn felipevillegas.wsgi` (start command)

Static files are served by WhiteNoise. Media files are stored in S3.

Set `DJANGO_SETTINGS_MODULE=config.settings.production` in the Railway environment along with all production variables from `.env.example`.
