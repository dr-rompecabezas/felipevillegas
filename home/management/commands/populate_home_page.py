"""
Management command to seed the HomePage StreamField content.

Usage:
    uv run python manage.py populate_home_page
    uv run python manage.py populate_home_page --force   # overwrite existing body
"""

import json

from django.core.management.base import BaseCommand

from home.models import HomePage

# ---------------------------------------------------------------------------
# StreamField body data
# ---------------------------------------------------------------------------
# Plain-text fields (CharBlock, TextBlock): & is fine as literal &
# RichTextBlock HTML: & must be &amp; so the stored HTML is valid
# ---------------------------------------------------------------------------

_ABOUT_HTML = (
    "<p>Twenty years ago I started building training programs for interpreters. "
    "Today I architect the LMS platforms, write the Django backends, and design the "
    "learning experiences — sometimes all three on the same project.</p>"
    "<p>My background spans instructional design, educational technology leadership, "
    "and full-stack software development. I've worked across higher education, "
    "healthcare, professional certification, and the non-profit sector. I build things "
    "that actually get used: a compliance training system serving 3,600 frontline "
    "workers annually, an exam platform with 94% test coverage, an open-source "
    "Wagtail LMS package on PyPI.</p>"
    "<p>What makes my work unusual is that the L&amp;D expertise and the technical "
    "capability aren't separate skill sets bolted together — they developed in "
    "parallel, each informing the other. I design with systems in mind and build "
    "with learners in mind.</p>"
    "<p>I'm based in Burlington, Ontario. My consulting practice is at "
    '<a href="https://thinkelearn.com">thinkelearn.com</a>. '
    "This site is where I keep my personal work: the software projects and the photography.</p>"
)

BODY = json.dumps(
    [
        {
            "type": "hero",
            "value": {
                "heading": "Felipe Villegas",
                "subtitle": (
                    "I design learning systems and build the platforms to deliver them "
                    "— twenty years in L&D, full-stack in Django."
                ),
                "cta_primary": {"text": "View My Work", "url": "/work/"},
                "cta_secondary": {"text": "Get in Touch", "url": "/contact/"},
            },
        },
        {
            "type": "about",
            "value": {"content": _ABOUT_HTML},
        },
        {
            "type": "featured_work",
            "value": {"heading": "Selected Work"},
        },
        {
            "type": "skills",
            "value": {
                "heading": "Core Capabilities",
                "skills": [
                    "Learning Technology & LMS Architecture",
                    "Instructional Design & eLearning Development",
                    "Django / Wagtail / Python",
                    "SCORM · xAPI · H5P",
                    "AWS · PostgreSQL · Railway",
                    "Applied AI for Learning Workflows",
                ],
            },
        },
        {
            "type": "contact_cta",
            "value": {
                "heading": "Let's talk",
                "message": (
                    "I'm currently open to Senior L&D, Learning Technology, and EdTech roles "
                    "— remote or hybrid in the GTA. Reach me at f.villegas@thinkelearn.com "
                    "or on LinkedIn."
                ),
            },
        },
    ]
)


class Command(BaseCommand):
    help = "Seed the HomePage StreamField with the launch content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite the body even if it already has content.",
        )

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("HomePage not found — run create_initial_pages first.")
            return

        if home.body and not options["force"]:
            self.stdout.write("HomePage body already has content. Use --force to overwrite.")
            return

        home.body = BODY
        home.save()
        self.stdout.write(self.style.SUCCESS("Done. HomePage body populated."))
