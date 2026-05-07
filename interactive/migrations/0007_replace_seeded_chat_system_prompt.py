"""Replace the previously-seeded chat_system_prompt with the slim style/scope frame.

Pages seeded by an earlier `populate_interactive_page` run carry a long
`chat_system_prompt` that includes an "About Felipe (factual context)"
section. Now that `interactive/data/profile.md` is the source of truth and
the view appends it to whatever the page prompt contains, that legacy
factual section duplicates and conflicts with the profile (different
phrasings, slightly different figures). This migration swaps the seeded
prompt for the new style/scope-only version on any page that still carries
it verbatim — pages that have been hand-edited in Wagtail admin are left
alone.

Both the live page row and the latest revision are patched, mirroring the
pattern used in 0004 so a subsequent edit-and-publish cannot resurrect the
old prompt from a stale revision.

The OLD and NEW strings are captured here verbatim on purpose: a migration
must keep working after the constants in `populate_interactive_page.py`
drift, so it pins the values it needs at the moment it ran.
"""

import json

from django.db import migrations

OLD_PROMPT = """You are a portfolio assistant for Felipe Villegas, a learning designer and technologist based in Burlington, Ontario.

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

NEW_PROMPT = """You are a portfolio assistant for Felipe Villegas, a learning designer and technologist based in Burlington, Ontario.

Your single job: answer questions from hiring managers, recruiters, and collaborators about Felipe's background, design philosophy, and approach to learning technology. Stay in scope.

A profile document with the full source of truth about Felipe — career history, projects, technical skills, education, certifications, honest scope notes, and out-of-scope topics — is appended below this prompt. Treat it as your factual basis. Do not invent details beyond what it contains.

Style:
- Two to four sentences. Plain language. Specific over vague.
- Quote concrete numbers, project names, and dates from the profile when they sharpen the answer; do not paraphrase them into vagueness.
- If a question is outside Felipe's work or his approach to learning technology — general L&D essays, comparative software opinions on tools he hasn't used, current events, hiring negotiation specifics — decline warmly and offer f.villegas@thinkelearn.com.
- Do not invent project details, dates, numbers, partners, clients, or quotes that are not in the profile. If the profile doesn't say it, you don't know it.
- Do not make promises or commitments on Felipe's behalf — direct those to the email above.
"""


def _parse(raw):
    """Accept dict (modern JSONField) or str (legacy text storage)."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _serialise_like(original, value):
    if isinstance(original, str):
        return json.dumps(value)
    return value


def _swap(current, want_from, want_to):
    """Return want_to if current matches want_from verbatim, else current."""
    return want_to if current == want_from else current


def _apply(apps, schema_editor, from_value, to_value):
    InteractivePage = apps.get_model("interactive", "InteractivePage")
    for page in InteractivePage.objects.all():
        new_value = _swap(page.chat_system_prompt, from_value, to_value)
        if new_value != page.chat_system_prompt:
            page.chat_system_prompt = new_value
            page.save(update_fields=["chat_system_prompt"])

    try:
        Revision = apps.get_model("wagtailcore", "Revision")
        ContentType = apps.get_model("contenttypes", "ContentType")
        ct = ContentType.objects.get(app_label="interactive", model="interactivepage")
    except (LookupError, Exception):
        return

    seen = set()
    for rev in Revision.objects.filter(content_type=ct).order_by("-created_at"):
        if rev.object_id in seen:
            continue
        seen.add(rev.object_id)

        content = _parse(rev.content)
        if not isinstance(content, dict):
            continue
        current = content.get("chat_system_prompt", "")
        new_value = _swap(current, from_value, to_value)
        if new_value != current:
            content["chat_system_prompt"] = new_value
            rev.content = _serialise_like(rev.content, content)
            rev.save(update_fields=["content"])


def forward(apps, schema_editor):
    _apply(apps, schema_editor, OLD_PROMPT, NEW_PROMPT)


def reverse(apps, schema_editor):
    _apply(apps, schema_editor, NEW_PROMPT, OLD_PROMPT)


class Migration(migrations.Migration):
    dependencies = [
        ("interactive", "0006_alter_interactivepage_chat_enabled_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
