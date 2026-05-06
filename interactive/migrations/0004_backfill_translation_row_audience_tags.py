"""Backfill audience_tags on translation_rows for pages created before Phase 2.

The schema change in 0003 made `audience_tags` an optional sub-block on
`TranslationRowBlock`. Pages already in the database (seeded by Phase 1) have
translation_rows JSON without that key, so the ?role= ordering and emphasis
features have nothing to match. This migration adds the tags to existing rows
in place — both on the live page row and on the page's latest revision so a
subsequent edit-and-publish doesn't blow the change away.

Pairings are duplicated from the populate command on purpose: a migration
must keep working after the constants in models.py / management commands
drift, so it captures the values it needs at the moment it ran.
"""

import json

from django.db import migrations

# Source of truth at migration time. Keep in sync with the populate command
# only insofar as new operators care; existing data is fixed once this runs.
AUDIENCE_TAGS_BY_QLUBPRO_FEATURE = {
    "Subdomain-based tenant isolation": ["lms_architect", "learning_engineer"],
    "Personalised player dashboard (matches, standings, challenges)": [
        "program_designer",
        "technical_id",
    ],
    "Role-based access (admin / captain / player)": [
        "program_designer",
        "lms_architect",
    ],
    "Enrollment windows, waitlists, and approval flows": [
        "program_designer",
        "lms_architect",
    ],
    "Rotating match schedule generation": ["learning_engineer", "technical_id"],
    "Score entry, dispute, and confirmation flows": [
        "technical_id",
        "program_designer",
    ],
    "Notification and nudge workflows": ["learning_engineer", "lms_architect"],
    "Season planner with standings and movement indicators": [
        "program_designer",
        "technical_id",
    ],
}


def _parse(raw):
    """Accept dict/list (modern JSONField) or str (legacy text storage)."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, (list, dict)):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _serialise_like(original, value):
    """Match the original storage shape so we don't accidentally rewrite type."""
    if isinstance(original, str):
        return json.dumps(value)
    return value


def _patch_blocks(blocks):
    """Mutate translation_row blocks in place; return True if anything changed."""
    if not isinstance(blocks, list):
        return False
    changed = False
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "translation_row":
            continue
        value = block.get("value")
        if not isinstance(value, dict):
            continue
        if value.get("audience_tags"):
            continue
        feature = value.get("qlubpro_feature")
        tags = AUDIENCE_TAGS_BY_QLUBPRO_FEATURE.get(feature)
        if tags:
            value["audience_tags"] = list(tags)
            changed = True
    return changed


def backfill(apps, schema_editor):
    InteractivePage = apps.get_model("interactive", "InteractivePage")

    for page in InteractivePage.objects.all():
        original = page.translation_rows
        blocks = _parse(original)
        if blocks is None:
            continue
        if _patch_blocks(blocks):
            page.translation_rows = _serialise_like(original, blocks)
            page.save(update_fields=["translation_rows"])

    # Patch the latest revision per page so re-publishing carries the change.
    try:
        Revision = apps.get_model("wagtailcore", "Revision")
    except LookupError:
        return
    try:
        ContentType = apps.get_model("contenttypes", "ContentType")
        ct = ContentType.objects.get(app_label="interactive", model="interactivepage")
    except Exception:
        return

    seen = set()
    revisions = Revision.objects.filter(content_type=ct).order_by("-created_at")
    for rev in revisions:
        if rev.object_id in seen:
            continue
        seen.add(rev.object_id)

        content = _parse(rev.content)
        if not isinstance(content, dict):
            continue
        rows_raw = content.get("translation_rows")
        rows = _parse(rows_raw)
        if rows is None:
            continue
        if _patch_blocks(rows):
            content["translation_rows"] = _serialise_like(rows_raw, rows)
            rev.content = _serialise_like(rev.content, content)
            rev.save(update_fields=["content"])


def reverse_noop(apps, schema_editor):
    """Reverse: leave the tags in place. Removing them would lose data."""
    return


class Migration(migrations.Migration):
    dependencies = [
        ("interactive", "0003_alter_interactivepage_translation_rows"),
    ]

    operations = [
        migrations.RunPython(backfill, reverse_noop),
    ]
