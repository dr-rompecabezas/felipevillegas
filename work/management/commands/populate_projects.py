"""
Management command to seed all portfolio projects into the Work section.

Usage:
    uv run python manage.py populate_projects
    uv run python manage.py populate_projects --force   # re-creates existing projects
"""

import json

from django.core.management.base import BaseCommand

from work.models import ProjectPage, TechTag, WorkIndexPage

# ---------------------------------------------------------------------------
# Tag definitions
# ---------------------------------------------------------------------------
TAG_SLUGS = [
    ("Django", "django"),
    ("Wagtail", "wagtail"),
    ("Python", "python"),
    ("PostgreSQL", "postgresql"),
    ("SCORM", "scorm"),
    ("xAPI", "xapi"),
    ("H5P", "h5p"),
    ("pandas", "pandas"),
    ("NumPy", "numpy"),
    ("Stripe", "stripe"),
    ("OAuth", "oauth"),
    ("HTMX", "htmx"),
    ("Alpine.js", "alpine-js"),
    ("GeoDjango", "geodjango"),
    ("PostGIS", "postgis"),
    ("Django REST Framework", "django-rest-framework"),
    ("FastAPI", "fastapi"),
    ("PyTorch", "pytorch"),
    ("Celery", "celery"),
    ("Redis", "redis"),
    ("Docker", "docker"),
    ("Moodle", "moodle"),
    ("AWS", "aws"),
    ("Mapbox GL JS", "mapbox-gl-js"),
    ("MediaPipe", "mediapipe"),
    ("Accredible", "accredible"),
    ("ClassMarker", "classmarker"),
    ("ProctorU", "proctoru"),
    ("Heroku", "heroku"),
    ("Zendesk", "zendesk"),
]


# ---------------------------------------------------------------------------
# Project definitions
# ---------------------------------------------------------------------------
def _rt(html: str) -> dict:
    """Wrap an HTML string as a rich_text StreamField block dict."""
    return {"type": "rich_text", "value": html}


PROJECTS = [
    {
        "title": "wagtail-lms",
        "slug": "wagtail-lms",
        "tagline": "Open-source Wagtail extension adding SCORM, H5P, and xAPI to any Django site.",
        "role": "Author & Maintainer",
        "client_context": "Open-source project published on PyPI",
        "status": "open_source",
        "primary_domain": "hybrid",
        "featured": True,
        "link_github": "https://github.com/dr-rompecabezas/wagtail-lms",
        "link_pypi": "https://pypi.org/project/wagtail-lms/",
        "link_live": "https://wagtail-lms.readthedocs.io/en/stable/",
        "tech_slugs": ["wagtail", "django", "python", "scorm", "xapi", "h5p"],
        "seo_title": "wagtail-lms — Open Source Django LMS Package",
        "search_description": (
            "Open-source package adding SCORM, H5P, and xAPI to Wagtail. "
            "Supports Django 4.2–6.0 and Python 3.11–3.14. "
            "Pluggable viewsets, MIT-licensed, published on PyPI."
        ),
        "outcome": (
            "Published to PyPI; supports Django 4.2–6.0 and Python 3.11–3.14 across a "
            "matrix-tested CI suite. Adopted in production at thinkelearn.com. Provides "
            "pluggable viewsets so teams can add SCORM and H5P delivery to any Wagtail "
            "site without forking."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>wagtail-lms is a reusable Django app that adds a full learning "
                    "management layer — SCORM 1.2/2004, H5P, and xAPI tracking — on top of "
                    "any Wagtail site. The project grew out of the infrastructure I built for "
                    "thinkelearn.com and was extracted into a standalone package to make the "
                    "same capability available to the wider community.</p>"
                    "<p>The architecture centres on pluggable viewsets, so developers can "
                    "mount the LMS URLs wherever they need them and override templates without "
                    "patching the library. A comprehensive test suite covers Django 4.2 through "
                    "6.0 and Python 3.11 through 3.14 via GitHub Actions matrix builds.</p>"
                    "<p>The package handles SCORM package upload, unzipping, manifest parsing, "
                    "and runtime communication (SCORM API JavaScript bridge), as well as H5P "
                    "content rendering and xAPI statement dispatch. It is MIT-licensed and "
                    "actively maintained.</p>"
                ),
            ]
        ),
    },
    {
        "title": "PDC Certification Portal",
        "slug": "pdc-portal",
        "tagline": "Greenfield certification management platform for a global designations body, built to production with 866 tests at 94% coverage.",
        "role": "Lead Developer",
        "client_context": "Professional Designations Corp — certification body for ITSM professionals",
        "status": "production",
        "primary_domain": "hybrid",
        "featured": True,
        "link_github": "",
        "link_live": "https://portal.professionaldesignations.com",
        "link_pypi": "",
        "tech_slugs": [
            "django",
            "python",
            "postgresql",
            "pandas",
            "numpy",
            "proctoru",
            "classmarker",
            "accredible",
            "heroku",
        ],
        "seo_title": "PDC Certification Portal — Django with 866 Tests",
        "search_description": (
            "Certification platform with ProctorU, ClassMarker, and Accredible integrations. "
            "866 unit tests at 94% coverage. Built in Django, deployed on Heroku."
        ),
        "outcome": (
            "866 unit tests at 94% coverage shipped to production. Three third-party "
            "integrations — ProctorU (remote proctoring), ClassMarker (online exams), and "
            "Accredible (digital credentials) — deployed and serving live candidates. "
            "Psychometric analysis pipeline built with pandas and NumPy for exam item review."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>Professional Designations Corp needed a modern replacement for a "
                    "legacy certification system. I designed and built the full application "
                    "from scratch: candidate registration, exam scheduling, remote proctoring "
                    "via ProctorU, exam delivery through ClassMarker, and automated digital "
                    "credential issuance via Accredible.</p>"
                    "<p>The data model handles multiple designation tracks, eligibility rules, "
                    "exam attempt limits, and result storage. A pandas/NumPy analysis pipeline "
                    "gives the psychometrics team per-item statistics (difficulty, discrimination "
                    "index, distractor analysis) as well as per-form performance metrics "
                    "(Cronbach's Alpha, standard deviation, standard error).</p>"
                    "<p>The test suite — 866 unit tests at 94% coverage — was written in "
                    "parallel with development. Each external integration (ProctorU, ClassMarker, "
                    "Accredible) is wrapped behind a service layer so it can be mocked cleanly "
                    "in tests and swapped in the future without touching business logic. "
                    "The application is deployed on Heroku with a managed PostgreSQL database.</p>"
                ),
            ]
        ),
    },
    {
        "title": "thinkelearn.com",
        "slug": "thinkelearn",
        "tagline": "Production Django + Wagtail platform delivering SCORM and H5P courses with Stripe billing and Google/Microsoft SSO.",
        "role": "Managing Director & Lead Developer",
        "client_context": "THINK eLearn Inc. — e-learning consultancy and course platform",
        "status": "production",
        "primary_domain": "hybrid",
        "featured": True,
        "link_github": "https://github.com/thinkelearn/thinkelearn",
        "link_live": "https://thinkelearn.com",
        "link_pypi": "",
        "tech_slugs": ["django", "wagtail", "python", "stripe", "oauth", "scorm", "h5p", "xapi", "postgresql"],
        "seo_title": "thinkelearn.com — Django + Wagtail Course Platform",
        "search_description": (
            "Production Django + Wagtail platform for SCORM and H5P course delivery, "
            "Stripe billing, and Google/Microsoft SSO. MIT-licensed — source available on GitHub."
        ),
        "outcome": (
            "Production site serving paying customers. First integration of wagtail-lms "
            "outside the author's own environment. Stripe billing, Google and Microsoft "
            "OAuth SSO, and SCORM/H5P content delivery all running on Railway with "
            "PostgreSQL and S3 media storage."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>thinkelearn.com is the commercial platform for THINK eLearn Inc., "
                    "the consultancy I run. The site is built on Django and Wagtail, with "
                    "content managed entirely through the Wagtail admin — no custom CMS "
                    "needed.</p>"
                    "<p>Course delivery is handled by wagtail-lms, the open-source package "
                    "I authored, which provides SCORM 1.2/2004 and H5P runtime support. "
                    "Stripe handles subscriptions and one-time purchases. OAuth SSO via "
                    "Google and Microsoft lets corporate learners sign in with their existing "
                    "accounts.</p>"
                    "<p>The project is MIT-licensed and the full source is public on GitHub, "
                    "making it one of the few real-world examples of wagtail-lms in a "
                    "production context. Infrastructure runs on Railway with PostgreSQL "
                    "and AWS S3 for media.</p>"
                ),
            ]
        ),
    },
    {
        "title": "QlubPro",
        "slug": "qlubpro",
        "tagline": "Multi-tenant SaaS for tennis league management with subdomain routing and contextvar-scoped query isolation.",
        "role": "Lead Developer",
        "client_context": "Tennis league operators and club administrators",
        "status": "production",
        "primary_domain": "software",
        "featured": True,
        "link_github": "",
        "link_live": "https://qlubpro.com",
        "link_pypi": "",
        "tech_slugs": ["django", "python", "postgresql", "htmx", "alpine-js"],
        "seo_title": "QlubPro — Multi-Tenant Django SaaS",
        "search_description": (
            "Multi-tenant SaaS for tennis leagues. Subdomain routing, contextvar-scoped "
            "query isolation, HTMX + Alpine.js. Live at qlubpro.com, built on Django 6."
        ),
        "outcome": (
            "Live multi-tenant SaaS at qlubpro.com running Django 6. Subdomain-based "
            "tenant resolution with contextvar query scoping provides complete data "
            "isolation between clubs without separate databases. HTMX and Alpine.js "
            "deliver a responsive UI with minimal JavaScript overhead."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>QlubPro is a multi-tenant SaaS application for tennis leagues and "
                    "clubs. Each club gets its own subdomain and a fully isolated data "
                    "environment — schedules, player rosters, match results, and standings "
                    "— without the complexity of separate databases per tenant.</p>"
                    "<p>Tenancy is resolved at the request level via subdomain and stored in "
                    "a Python contextvar, which is then used to scope all querysets "
                    "automatically. This approach keeps business logic clean: views and "
                    "models don't need to pass a tenant object around; the middleware and "
                    "a custom manager handle isolation transparently.</p>"
                    "<p>The frontend uses HTMX for partial page updates and Alpine.js for "
                    "lightweight client-side state, keeping the JavaScript footprint small "
                    "while still delivering a modern, responsive experience. Built on "
                    "Django 6 and deployed on Railway.</p>"
                ),
            ]
        ),
    },
    {
        "title": "CFAS Portal MVP",
        "slug": "cfas-portal-mvp",
        "tagline": "Full-stack bilingual demo built in 7 days for a competitive RFP — GeoDjango, Stripe, Wagtail, and DRF.",
        "role": "Lead Developer",
        "client_context": "Canadian Fertility & Andrology Society — RFP for a member services portal",
        "status": "archived",
        "primary_domain": "hybrid",
        "featured": False,
        "link_github": "",
        "link_live": "",
        "link_pypi": "",
        "tech_slugs": [
            "django",
            "wagtail",
            "python",
            "postgresql",
            "geodjango",
            "postgis",
            "django-rest-framework",
            "stripe",
            "mapbox-gl-js",
        ],
        "seo_title": "CFAS Portal MVP — Bilingual Django RFP Prototype",
        "search_description": (
            "Bilingual Django prototype built in 7 days for a competitive RFP. "
            "GeoDjango, PostGIS, Mapbox GL JS, Stripe, and DRF — deployed for a live demonstration."
        ),
        "outcome": (
            "Competitive RFP prototype delivered in 7 days. Demonstrated bilingual "
            "(EN/FR) Wagtail CMS, GeoDjango/PostGIS spatial queries with Mapbox GL JS "
            "visualisation, Stripe payment integration, and a DRF API — all in a single "
            "deployable codebase."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>When the Canadian Fertility &amp; Andrology Society issued an RFP "
                    "for a new member services portal, I had one week to build a working "
                    "prototype. The demo needed to show bilingual content management, "
                    "interactive maps, secure payments, and an API — not wireframes, but "
                    "running software.</p>"
                    "<p>The stack: Wagtail for CMS with Django Modeltranslation for EN/FR "
                    "content, GeoDjango and PostGIS for spatial data, Mapbox GL JS for map "
                    "rendering, Stripe for payment flows, and Django REST Framework for the "
                    "data API. Everything was containerised and deployed for the live "
                    "demonstration.</p>"
                    "<p>The project is archived — the RFP process concluded — but it "
                    "remains a useful reference for how quickly a complex, multi-capability "
                    "Django application can be stood up when the stack is well understood.</p>"
                ),
            ]
        ),
    },
    {
        "title": "Omdena — Urban Tree Observatory",
        "slug": "urban-tree-observatory",
        "tagline": "GIS web app seeding 1M+ records from CSV to PostGIS, built with a distributed volunteer team.",
        "role": "Lead ML Engineer",
        "client_context": "Omdena Gibdet Colombia Chapter — civic GIS project",
        "status": "archived",
        "primary_domain": "software",
        "featured": False,
        "link_github": "https://github.com/OmdenaAI/GibdetColombiaChapter_UrbanTreeObservatory",
        "link_live": "",
        "link_pypi": "",
        "tech_slugs": ["django", "python", "postgresql", "geodjango", "postgis", "django-rest-framework", "docker"],
        "seo_title": "Urban Tree Observatory — GeoDjango GIS App",
        "search_description": (
            "GeoDjango/PostGIS/DRF web app for urban tree mapping. "
            "Bulk-loads 1M+ biodiversity records from CSV to PostGIS. "
            "Recognised as Lead ML Engineer by Omdena."
        ),
        "outcome": (
            "Management command seeding 1M+ biodiversity records from flat CSV files into "
            "PostGIS in a single run. Django/GeoDjango/DRF API serving spatial queries "
            "to a map frontend. Recognised as Lead ML Engineer by Omdena for "
            "contributions to the project."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>The Urban Tree Observatory is a civic GIS project mapping the urban "
                    "tree canopy of Ibagué, Colombia. The data challenge was bulk-loading "
                    "over one million tree records — each with species, coordinates, and "
                    "condition attributes — from flat CSV files into a PostGIS database "
                    "efficiently and repeatably.</p>"
                    "<p>I wrote the Django management command that reads the source CSVs, "
                    "validates and transforms each row, and bulk-inserts records using "
                    "`bulk_create` in configurable batch sizes. On a standard dev machine "
                    "the full 1M-row load completes in minutes rather than hours.</p>"
                    "<p>The backend is Django + GeoDjango + DRF, exposing a spatial API "
                    "that powers the map visualisation. The project was built with a "
                    "distributed volunteer engineering team through Omdena's collaborative "
                    "AI programme. I was recognised as Lead ML Engineer for my contributions.</p>"
                ),
            ]
        ),
    },
    {
        "title": "Omdena — VisionVitals",
        "slug": "visionvitals",
        "tagline": "Computer vision health monitoring app combining Django, FastAPI, MediaPipe, and PyTorch in a single inference pipeline.",
        "role": "Backend Engineer",
        "client_context": "Omdena collaborative AI project — computer vision health monitoring",
        "status": "archived",
        "primary_domain": "software",
        "featured": False,
        "link_github": "",
        "link_live": "",
        "link_pypi": "",
        "tech_slugs": ["django", "python", "django-rest-framework", "fastapi", "pytorch", "celery", "mediapipe"],
        "seo_title": "VisionVitals — Computer Vision Health Monitoring",
        "search_description": (
            "Computer vision health monitoring: Django + DRF API, FastAPI microservice "
            "for MediaPipe/PyTorch inference, Celery task queue. Omdena collaborative AI project."
        ),
        "outcome": (
            "End-to-end AI inference pipeline: Django REST API receives video frames, "
            "Celery queues inference tasks, FastAPI microservice runs MediaPipe pose "
            "estimation and PyTorch classification, results returned asynchronously. "
            "Architecture decouples ML inference from the web layer for independent scaling."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>VisionVitals is a health monitoring application that analyses a subject's "
                    "face and hand from video input using computer vision models to measure vital "
                    "signs. The engineering challenge was integrating a GPU-accelerated PyTorch "
                    "inference model into a web application without blocking request threads "
                    "or coupling the ML environment to the Django process.</p>"
                    "<p>The architecture separates concerns into three layers: a Django + DRF "
                    "web API that accepts uploads and returns results; a Celery task queue "
                    "that dispatches inference jobs; and a FastAPI microservice that hosts "
                    "the MediaPipe pose estimation and PyTorch classification pipeline and "
                    "can be scaled or redeployed independently of the web tier.</p>"
                    "<p>Built as part of an Omdena collaborative project with a distributed "
                    "international team.</p>"
                ),
            ]
        ),
    },
    {
        "title": "Omdena — CropCycle",
        "slug": "cropcycle",
        "tagline": "Django + FastAPI microservice architecture for ML crop-cycle prediction, with Redis task queuing and PostgreSQL.",
        "role": "Backend Engineer",
        "client_context": "Omdena collaborative AI project — agricultural ML",
        "status": "archived",
        "primary_domain": "software",
        "featured": False,
        "link_github": "",
        "link_live": "",
        "link_pypi": "",
        "tech_slugs": ["django", "python", "django-rest-framework", "fastapi", "pytorch", "postgresql", "redis"],
        "seo_title": "CropCycle — Django + FastAPI ML Microservices",
        "search_description": (
            "ML crop-cycle prediction with Django + DRF, FastAPI microservice for PyTorch inference, "
            "and a Redis task queue. Agricultural AI project from Omdena."
        ),
        "outcome": (
            "ML crop-cycle prediction model served via FastAPI microservice, integrated "
            "with a Django REST Framework API and Redis-backed task queue. Asynchronous "
            "job pattern allows long-running model inference without HTTP timeouts."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>CropCycle is an agricultural machine learning project predicting "
                    "optimal planting and harvest windows from climate and soil data. The "
                    "backend architecture follows the same microservice pattern I used in "
                    "VisionVitals: a Django + DRF API as the primary interface, a FastAPI "
                    "service hosting the PyTorch model, and Redis managing the task queue "
                    "between them.</p>"
                    "<p>This separation means the ML environment (Python version, CUDA "
                    "dependencies, model weights) can be versioned and deployed independently "
                    "of the web application. Redis provides the job broker; Celery workers "
                    "in the FastAPI service pick up inference tasks and write results back "
                    "to PostgreSQL.</p>"
                    "<p>Built with an Omdena distributed team; my focus was the backend "
                    "service integration layer.</p>"
                ),
            ]
        ),
    },
    {
        "title": "College of Physiotherapists LMS",
        "slug": "copt-lms",
        "tagline": "Enterprise Moodle LMS on AWS for 9,000 regulated health professionals, with automated compliance tracking and Zendesk support.",
        "role": "Learning Technology Manager",
        "client_context": "College of Physiotherapists of Ontario — regulatory body for physiotherapists",
        "status": "archived",
        "primary_domain": "ld",
        "featured": False,
        "link_github": "",
        "link_live": "",
        "link_pypi": "",
        "tech_slugs": ["moodle", "aws", "zendesk"],
        "seo_title": "College of Physiotherapists LMS — Enterprise Moodle on AWS",
        "search_description": (
            "Enterprise Moodle on AWS for 9,000 regulated physiotherapists. "
            "Automated compliance tracking, Zendesk integration, and custom reporting for the registrar."
        ),
        "outcome": (
            "Enterprise Moodle platform serving 9,000 regulated members on AWS. "
            "Automated compliance tracking replaced manual tracking process. "
            "Zendesk integration provided member-facing support with measurable "
            "ticket resolution SLAs. Custom reporting gave the registrar real-time "
            "visibility into continuing competency completion rates."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>The College of Physiotherapists of Ontario required a scalable LMS "
                    "to administer an annual recertification exam to its 9,000 regulated members "
                    "province-wide. I deployed and managed the platform — Moodle on AWS — "
                    "from infrastructure configuration through to the member-facing "
                    "certification experience.</p>"
                    "<p>The most operationally significant work was replacing manual "
                    "compliance tracking with an automated system: enrolment, completion, "
                    "and deadline data flowed from Moodle into reports the registrar's "
                    "office could act on directly, eliminating a spreadsheet-heavy process "
                    "that was both slow and error-prone.</p>"
                    "<p>Member support ran through Zendesk. Custom reports were built for the "
                    "professional practice team to monitor completion rates by cohort and flag "
                    "members approaching compliance deadlines.</p>"
                ),
            ]
        ),
    },
    {
        "title": "felipevillegas.com",
        "slug": "felipevillegas-com",
        "tagline": "Personal portfolio built with Django and Wagtail — open source, MIT-licensed, and deployed on Railway.",
        "role": "Author & Developer",
        "client_context": "Personal professional portfolio — open source, public on GitHub",
        "status": "production",
        "primary_domain": "software",
        "featured": True,
        "link_github": "https://github.com/dr-rompecabezas/felipevillegas",
        "link_live": "https://felipevillegas.com",
        "link_pypi": "",
        "tech_slugs": ["django", "wagtail", "python", "postgresql", "aws"],
        "seo_title": "felipevillegas.com — Django + Wagtail Portfolio",
        "search_description": (
            "Personal portfolio built with Django 6 and Wagtail 7, deployed on Railway. "
            "MIT-licensed and open source — a reference implementation for production Wagtail."
        ),
        "outcome": (
            "Production site on Railway with PostgreSQL and AWS S3 for media. "
            "Open source under MIT licence — serves as a reference implementation "
            "for a production-grade Wagtail project: split settings, management-command "
            "content seeding, Tailwind CLI build, and a Railway deployment configuration "
            "with migrations as a release command."
        ),
        "body": json.dumps(
            [
                _rt(
                    "<p>This site is itself a portfolio project. It is built on Django 6 "
                    "and Wagtail 7, with Tailwind CSS for styling, WhiteNoise for static "
                    "file serving, and AWS S3 for media storage. Deployed on Railway with "
                    "a managed PostgreSQL database.</p>"
                    "<p>The codebase is MIT-licensed and publicly available on GitHub. "
                    "It doubles as a reference implementation for a clean, production-grade "
                    "Wagtail project: split settings for dev and production, management "
                    "commands for content seeding, a Tailwind CLI build pipeline, and a "
                    "Railway deployment configuration with migrations as a release command.</p>"
                    "<p>Page content is managed entirely through the Wagtail admin — no "
                    "hardcoded templates for page text. The Work, Photography, and Contact "
                    "sections are Wagtail page models with enforced parent/child constraints.</p>"
                ),
            ]
        ),
    },
]


class Command(BaseCommand):
    help = "Seed portfolio project pages into the Work section."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete and re-create any projects that already exist.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        work_index = WorkIndexPage.objects.first()
        if work_index is None:
            self.stderr.write("WorkIndexPage not found — run create_initial_pages first.")
            return

        # Ensure all TechTags exist.
        tags = {}
        for name, slug in TAG_SLUGS:
            tag, created = TechTag.objects.get_or_create(slug=slug, defaults={"name": name})
            tags[slug] = tag
            if created:
                self.stdout.write(f"  Created TechTag: {name}")

        created_count = 0
        skipped_count = 0

        for data in PROJECTS:
            slug = data["slug"]
            existing = ProjectPage.objects.child_of(work_index).filter(slug=slug).first()

            if existing:
                if force:
                    existing.delete()
                    self.stdout.write(f"  Deleted existing project: {slug}")
                else:
                    self.stdout.write(f"  Skipping (already exists): {slug}")
                    skipped_count += 1
                    continue

            tech_slugs = data["tech_slugs"]

            page = ProjectPage(
                title=data["title"],
                slug=data["slug"],
                tagline=data["tagline"],
                role=data["role"],
                client_context=data["client_context"],
                status=data["status"],
                primary_domain=data["primary_domain"],
                featured=data["featured"],
                link_github=data.get("link_github", ""),
                link_live=data.get("link_live", ""),
                link_pypi=data.get("link_pypi", ""),
                seo_title=data.get("seo_title", ""),
                search_description=data.get("search_description", ""),
                outcome=data["outcome"],
                body=data["body"],
                live=False,
            )
            work_index.add_child(instance=page)
            page.tech_stack.set([tags[s] for s in tech_slugs if s in tags])
            page.save_revision().publish()

            created_count += 1
            self.stdout.write(f"  Created ProjectPage: {page.title}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} project(s) created, {skipped_count} skipped."))
