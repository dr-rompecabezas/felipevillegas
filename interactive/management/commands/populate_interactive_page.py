"""
Management command to seed the InteractivePage with default content.

Usage:
    uv run python manage.py populate_interactive_page
    uv run python manage.py populate_interactive_page --force   # overwrite existing fields
"""

import json

from django.core.management.base import BaseCommand

from home.models import HomePage
from interactive.models import InteractivePage

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
HERO_KICKER = "Portfolio · Interactive"
HERO_STATEMENT_HTML = (
    "<p>A learning experience about a learning designer.</p>"
    "<p>You are the learner. The content is one candidate's case for the work. "
    "Each section below is a designed module — read it the way you would a "
    "course you were evaluating, not a CV.</p>"
)

# ---------------------------------------------------------------------------
# Timeline — twenty years to this moment
# ---------------------------------------------------------------------------
TIMELINE_NODES = [
    {
        "year": "2005",
        "label": "First e-learning platform",
        "body": (
            "<p>At MCIS Language Services, I launched the organisation's first e-learning "
            "platform on Moodle, serving 2,000+ working interpreters across Canada. Moving "
            "foundational content online — ethics, terminology, code of conduct — reclaimed "
            "classroom time for what actually had to happen face to face: role-play, "
            "simulated medical and legal cases, the applied practice that professional "
            "interpreting depends on.</p>"
        ),
        "audience_tags": ["generic", "technical_id", "lms_architect"],
    },
    {
        "year": "2012",
        "label": "Teaching the teachers",
        "body": (
            "<p>At Sheridan College I managed up to 40 continuing-education course "
            "development projects simultaneously and coached around 50 faculty on "
            "instructional design fundamentals. I introduced the Quality Matters® rubric "
            "as the college-wide quality standard and built the standardised D2L "
            "templates that gave the program its visual and structural consistency.</p>"
        ),
        "audience_tags": ["generic", "technical_id", "program_designer"],
    },
    {
        "year": "2015",
        "label": "Provincial scale",
        "body": (
            "<p>OntarioLearn's 1,800-course inventory served 70,000 students annually "
            "across 24 community colleges. I designed and led the QA Compatibility "
            "framework — evaluation rubrics, processes, training materials, and a "
            "MS Access workflow database — and used it to recommend corrective action "
            "on 112 courses based on student-feedback analysis.</p>"
        ),
        "audience_tags": ["generic", "lms_architect", "technical_id", "program_designer"],
    },
    {
        "year": "2017",
        "label": "Product leadership",
        "body": (
            "<p>As Director of Product Management at Pink Elephant, I led the development "
            "of 25 new education and certification products and grew the e-learning line "
            "of business 52% year over year. I worked across distributed teams in 15 "
            "time zones and managed external relations with the certification bodies "
            "(APMG, AXELOS, PeopleCert, DevOps Institute, EXIN) the company depended on.</p>"
        ),
        "audience_tags": ["generic", "program_designer"],
    },
    {
        "year": "2020",
        "label": "Pandemic pivot — to code",
        "body": (
            "<p>During COVID I worked through the freeCodeCamp full-stack curriculum end "
            "to end: responsive web design, JavaScript and data structures, front-end "
            "libraries, back-end microservices, data analysis with Python and pandas, "
            "machine learning with TensorFlow, scientific computing, information security. "
            "Ten certifications. The first commit. After two decades coordinating "
            "instructional designers, subject-matter experts, and multimedia producers, "
            "the shift to building the software myself.</p>"
        ),
        "audience_tags": ["generic", "learning_engineer"],
    },
    {
        "year": "2022",
        "label": "First production application",
        "body": (
            "<p>The PDC Portal began as a single webhook receiver and grew into a Django "
            "application that automated nearly every part of certification operations: "
            "candidate registration, exam scheduling, ProctorU, ClassMarker, Accredible, "
            "psychometric reporting. 866 unit tests at 94% coverage, written alongside "
            "the code, not after. This is where the discipline came from.</p>"
        ),
        "audience_tags": ["generic", "learning_engineer", "lms_architect"],
    },
    {
        "year": "2024",
        "label": "Building with AI",
        "body": (
            "<p>The year AI-assisted development became daily practice. Claude Code, "
            "Codex, and Copilot in the editor loop alongside the work itself. The point "
            "isn't the tools; it's the engineering discipline of using them well. "
            "Reading every diff. Writing the tests first. Treating the model like a fast "
            "junior engineer whose output needs review, not a black box that emits "
            "answers.</p>"
        ),
        "audience_tags": ["generic", "learning_engineer"],
    },
    {
        "year": "2025",
        "label": "The year things shipped",
        "body": (
            "<p>Many forms, parallel work. <em>wagtail-lms</em> on PyPI in October — "
            "matrix-tested support across Django 4.2–6.0 and Python 3.11–3.14. "
            "<em>QlubPro</em> built out as a multi-tenant Django SaaS for tennis leagues "
            "with subdomain tenancy and ContextVar-scoped query isolation. Two competitive "
            "RFP prototypes in seven days each: <em>CTCMPAO Learning Hub</em> (site "
            "crawling, PDF extraction, canonical knowledge documents) and <em>CFAS Portal "
            "MVP</em> (bilingual Django, GeoDjango, Stripe, DRF). Three Omdena collaborations: "
            "<em>Urban Tree Observatory</em> (recognised as Lead ML Engineer for the "
            "1M-record PostGIS bulk-load), <em>VisionVitals</em>, and <em>CropCycle</em>. "
            "And the IBM RAG &amp; Agentic AI Professional Certificate, eight Coursera "
            "courses, completed Sep–Oct.</p>"
        ),
        "audience_tags": ["generic", "learning_engineer", "lms_architect"],
    },
    {
        "year": "2026",
        "label": "This page",
        "body": (
            "<p>Built as part of an application for a senior role at the intersection "
            "of learning design and engineering. The page is the argument: a learning "
            "designer who can also build the technology can demonstrate the capability "
            "by building the application experience itself.</p>"
        ),
        "audience_tags": ["generic"],
    },
]

# ---------------------------------------------------------------------------
# QlubPro → learning platform translation
# ---------------------------------------------------------------------------
TRANSLATION_ROWS = [
    {
        "qlubpro_feature": "Subdomain-based tenant isolation",
        "learning_equivalent": "Multi-org LMS architecture",
        "commentary": (
            "<p>Each club resolves at the request layer via subdomain; a Python "
            "ContextVar carries the tenant through the request lifecycle so every "
            "queryset is scoped automatically. The same pattern lets a single LMS "
            "host many client orgs without duplicate databases or special-case code.</p>"
        ),
        "audience_tags": ["lms_architect", "learning_engineer"],
    },
    {
        "qlubpro_feature": "Personalised player dashboard (matches, standings, challenges)",
        "learning_equivalent": "Learner dashboard (modules, progress, next steps)",
        "commentary": (
            "<p>The dashboard surfaces only what's actionable for the visitor "
            "<em>right now</em>. It's the same design discipline a good learner home "
            "page needs: not a list of everything, but a short list of what to do next.</p>"
        ),
        "audience_tags": ["program_designer", "technical_id"],
    },
    {
        "qlubpro_feature": "Role-based access (admin / captain / player)",
        "learning_equivalent": "Role-based learning paths (new hire / manager / senior leader)",
        "commentary": (
            "<p>Permissions and content visibility branch on role at the model layer, "
            "not just the template. That's how an LMS keeps a senior leader's path "
            "clean of new-hire onboarding while still letting them drop in if needed.</p>"
        ),
        "audience_tags": ["program_designer", "lms_architect"],
    },
    {
        "qlubpro_feature": "Enrollment windows, waitlists, and approval flows",
        "learning_equivalent": "Program enrollment with prerequisites and gating",
        "commentary": (
            "<p>The state machine is what matters: open → waitlist → approved → "
            "enrolled → completed, with the right notification at every transition. "
            "Same shape, different domain.</p>"
        ),
        "audience_tags": ["program_designer", "lms_architect"],
    },
    {
        "qlubpro_feature": "Rotating match schedule generation",
        "learning_equivalent": "Adaptive content sequencing",
        "commentary": (
            "<p>Both are constraint-satisfaction problems dressed up as scheduling. "
            "The hard part isn't the algorithm — it's the override and exception "
            "handling that lets a human intervene without breaking the model.</p>"
        ),
        "audience_tags": ["learning_engineer", "technical_id"],
    },
    {
        "qlubpro_feature": "Score entry, dispute, and confirmation flows",
        "learning_equivalent": "Formative assessment with feedback loops",
        "commentary": (
            "<p>Submission → review → confirmation isn't just a sports rule, it's "
            "the structure of a feedback loop that respects the learner. The dispute "
            "path is what separates a real assessment system from a quiz.</p>"
        ),
        "audience_tags": ["technical_id", "program_designer"],
    },
    {
        "qlubpro_feature": "Notification and nudge workflows",
        "learning_equivalent": "Spaced repetition and learning reminders",
        "commentary": (
            "<p>Celery for the schedule, templates for the message, opt-out for the "
            "respect. The hardest part is restraint: every nudge that doesn't add "
            "value erodes the channel for the ones that do.</p>"
        ),
        "audience_tags": ["learning_engineer", "lms_architect"],
    },
    {
        "qlubpro_feature": "Season planner with standings and movement indicators",
        "learning_equivalent": "Curriculum roadmap with progress tracking",
        "commentary": (
            "<p>Visible progress and visible direction. A player should know where "
            "they stand and where they're headed; so should a learner. The data model "
            "is nearly identical.</p>"
        ),
        "audience_tags": ["program_designer", "technical_id"],
    },
]

# ---------------------------------------------------------------------------
# AI in practice — three projects
# ---------------------------------------------------------------------------
AI_CARDS = [
    {
        "title": "CTCMPAO Learning Hub — 7-day RFP prototype",
        "summary": (
            "<p>For the College of Traditional Chinese Medicine Practitioners and "
            "Acupuncturists of Ontario: a working Django + Wagtail learning hub built "
            "in a week as part of an RFP response. Three layers: site crawling and "
            "PDF extraction, canonical knowledge documents with classification and "
            "chunking, and a Wagtail-rendered practitioner-facing hub with search and "
            "Standards-of-Practice links. SCORM and H5P content embedding via "
            "wagtail-lms. Portfolio prototype, not maintained.</p>"
        ),
        "link": "https://ctcmpao-hub-demo.up.railway.app/",
        "link_label": "View the demo",
    },
    {
        "title": "QuGenAI and AI Roleplay Trainer",
        "summary": (
            "<p>Two prototype-scale tools from 2025. QuGenAI generates quiz items "
            "from source documents; the Roleplay Trainer runs scenario-based "
            "conversational practice. Built with LangChain, the OpenAI API, and "
            "Streamlit. Proof-of-concept scale, real instructional-design thinking — "
            "the prompt structure is the lesson plan.</p>"
        ),
        "link": "",
        "link_label": "",
    },
    {
        "title": "IBM RAG & Agentic AI Professional Certificate",
        "summary": (
            "<p>Eight-course Coursera series completed in 2025. Coverage: LangChain "
            "fundamentals, multimodal generative AI applications, advanced RAG with "
            "FAISS and HNSW, vector databases (ChromaDB), LlamaIndex RAG, "
            "LangGraph agentic patterns (ReAct, Reflexion, tool calling), and "
            "multi-agent systems with CrewAI, AutoGen, and BeeAI.</p>"
        ),
        "link": "",
        "link_label": "",
    },
]

# ---------------------------------------------------------------------------
# Reflection — small interactive beat
# ---------------------------------------------------------------------------
REFLECTION = {
    "prompt": (
        "Which of these patterns do you most need on your team right now? "
        "(The page will lean into your pick as you keep scrolling.)"
    ),
    "options": [
        "Multi-tenant LMS architecture",
        "Learner dashboards that focus attention",
        "Role-based learning paths",
        "Adaptive content sequencing",
        "Feedback loops with real assessment",
        "Curriculum roadmap visibility",
    ],
}

# ---------------------------------------------------------------------------
# Closing
# ---------------------------------------------------------------------------
CLOSING_HTML = (
    "<p>This site is the long-form version. The page above is the live version. "
    "If you're hiring for a role at the intersection of learning design and "
    "engineering, I'd like to talk.</p>"
    "<p>"
    '<a href="mailto:f.villegas@thinkelearn.com">f.villegas@thinkelearn.com</a>'
    " &middot; "
    '<a href="https://linkedin.com/in/felipevillegas">LinkedIn</a>'
    " &middot; "
    '<a href="https://thinkelearn.com">thinkelearn.com</a>'
    "</p>"
)

# ---------------------------------------------------------------------------
# Chat system prompt — Phase 3 will wire this up; Felipe to review before going live
# ---------------------------------------------------------------------------
CHAT_SYSTEM_PROMPT = """You are a portfolio assistant for Felipe Villegas, a learning designer and technologist based in Burlington, Ontario.

Your single job: answer questions from hiring managers, recruiters, and collaborators about Felipe's background, design philosophy, and approach to learning technology. Stay in scope.

About Felipe (factual context — do not add to or invent beyond this):
- 20+ years in learning design, LMS administration, and educational technology, with a parallel 3-year intensive Django/Wagtail engineering track.
- Selected roles: MCIS Language Services (2005-2012, manager — launched the org's first e-learning platform, 2,000+ learners); Sheridan College (2012-2014, project manager, 40+ simultaneous course-development projects, coached ~50 instructors); OntarioLearn (2015-2017, QA framework across 24 colleges, ~70,000 students); Pink Elephant (2017-2020, Director of Product Management — 25 new products, 52% YoY e-learning revenue growth); Professional Designations (2022-2025, technical lead — built PDC Portal, 866 tests at 94% coverage); THINK eLearn (2014-present, partner and technical lead).
- Education: MA, Learning and Technology, Royal Roads University. BA, Communication and Journalism, UNAD Colombia. Certified Fullstack Developer, freeCodeCamp.
- Selected current technical work: QlubPro (production multi-tenant Django SaaS for tennis leagues; first client Burlington Tennis Club; 900+ tests; subdomain tenancy with ContextVar query scoping); wagtail-lms (open-source PyPI package adding SCORM/H5P/xAPI to any Wagtail site); thinkelearn.com (production Django + Wagtail platform); felipevillegas.com (this site, Django + Wagtail, MIT-licensed, public on GitHub).
- AI work: CTCMPAO Learning Hub 7-day RFP prototype (2026) — site crawling, PDF extraction, canonical knowledge documents, Wagtail CMS; QuGenAI and AI Roleplay Trainer (2025, prototypes); IBM RAG & Agentic AI Professional Certificate (Coursera, 2025, 8 courses).
- Contact: f.villegas@thinkelearn.com.

Style:
- Two to four sentences. Plain language. Specific over vague.
- If a question is outside this scope (general L&D essays, comparative software opinions, current events, anything not about Felipe's work or his approach to learning technology), decline warmly and offer the email above.
- Do not invent project details, dates, numbers, or quotes that are not in this brief.
- Do not make promises or commitments on Felipe's behalf.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _stream(block_type: str, items: list) -> str:
    return json.dumps([{"type": block_type, "value": item} for item in items])


def _build_field_payload() -> dict:
    return {
        "hero_kicker": HERO_KICKER,
        "hero_statement": HERO_STATEMENT_HTML,
        "timeline_nodes": _stream("timeline_node", TIMELINE_NODES),
        "translation_rows": _stream("translation_row", TRANSLATION_ROWS),
        "ai_cards": _stream("ai_card", AI_CARDS),
        "reflection": _stream("reflection", [REFLECTION]),
        "closing_paragraph": CLOSING_HTML,
        "chat_system_prompt": CHAT_SYSTEM_PROMPT,
    }


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------
class Command(BaseCommand):
    help = "Seed (or refresh with --force) the InteractivePage at /interactive/."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite content fields even when the page already exists.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("HomePage not found — run create_initial_pages first.")
            return

        page = InteractivePage.objects.first()
        payload = _build_field_payload()

        if page is None:
            page = InteractivePage(
                title="Interactive",
                slug="interactive",
                live=True,
                **payload,
            )
            home.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Created InteractivePage at /interactive/."))
            return

        if not force:
            self.stdout.write("InteractivePage already exists. Use --force to overwrite content fields.")
            return

        for field, value in payload.items():
            setattr(page, field, value)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("  Updated InteractivePage content fields."))
