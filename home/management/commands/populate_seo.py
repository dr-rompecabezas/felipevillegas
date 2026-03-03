"""
Management command to set seo_title and search_description on the four
static/index pages (HomePage, WorkIndexPage, PhotographyIndexPage, ContactPage).

The base template appends "| Felipe Villegas" to seo_title, so these values
are short descriptors that produce clean title tags, e.g.:
    "Learning Design & Technology | Felipe Villegas"

Usage:
    uv run python manage.py populate_seo
    uv run python manage.py populate_seo --force   # overwrite existing values
"""

from django.core.management.base import BaseCommand

from contact.models import ContactPage
from home.models import HomePage
from photography.models import PhotographyIndexPage
from work.models import WorkIndexPage

PAGES = [
    {
        "model": HomePage,
        "seo_title": "Learning Design & Technology",
        "search_description": (
            "Felipe Villegas designs learning systems and builds the platforms to deliver them "
            "— 20 years in L&D, full-stack in Django. Based in Burlington, Ontario."
        ),
    },
    {
        "model": WorkIndexPage,
        "seo_title": "Work",
        "search_description": (
            "Software and L&D portfolio: open-source Django packages, production SaaS, "
            "certification platforms, and enterprise LMS deployments. Filter by domain."
        ),
    },
    {
        "model": PhotographyIndexPage,
        "seo_title": "Photography",
        "search_description": (
            "Photography by Felipe Villegas — landscape, urban, and event galleries from around the world."
        ),
    },
    {
        "model": ContactPage,
        "seo_title": "Contact",
        "search_description": (
            "Get in touch with Felipe Villegas — open to Senior L&D, Learning Technology, "
            "and EdTech roles. Remote or hybrid in the GTA."
        ),
    },
]


class Command(BaseCommand):
    help = "Set seo_title and search_description on the four static/index pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing SEO values.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        for entry in PAGES:
            model = entry["model"]
            page = model.objects.first()

            if page is None:
                self.stderr.write(f"  {model.__name__} not found — run create_initial_pages first.")
                continue

            if page.seo_title and not force:
                self.stdout.write(f"  Skipping {model.__name__} (already set). Use --force to overwrite.")
                continue

            page.seo_title = entry["seo_title"]
            page.search_description = entry["search_description"]
            page.save()
            self.stdout.write(f"  {model.__name__}: '{page.seo_title}'")

        self.stdout.write(self.style.SUCCESS("Done."))
