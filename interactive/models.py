from django.core.validators import RegexValidator
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

AUDIENCE_FOCUS_CHOICES = [
    ("generic", "Generic"),
    ("program_designer", "Program Experience Designer"),
    ("lms_architect", "Learning Technology / LMS Architect"),
    ("learning_engineer", "Learning Engineer"),
    ("technical_id", "Technical Instructional Designer"),
]

AUDIENCE_FOCUS_VALUES = {value for value, _ in AUDIENCE_FOCUS_CHOICES}


def audience_focus_to_url(value: str) -> str:
    """Internal value (program_designer) → URL slug (program-designer)."""
    return value.replace("_", "-")


def audience_focus_from_url(slug: str) -> str | None:
    """URL slug → internal value, or None if unknown.

    Accepts dashed (program-designer) and underscored (program_designer) forms,
    case-insensitive. Returns None when the slug is empty or doesn't map to a
    known audience focus.
    """
    if not slug:
        return None
    candidate = slug.strip().lower().replace("-", "_")
    return candidate if candidate in AUDIENCE_FOCUS_VALUES else None


# Reflection options are framed in reader-conversational language; translation
# rows are framed in domain-specific language. This mapping is the deliberate
# editorial pairing between the two — option text → translation row's
# `qlubpro_feature` (the row's stable identity within the StreamField).
# Edit here to re-pair an option with a different row.
REFLECTION_OPTION_TO_ROW_KEY = {
    "Multi-tenant LMS architecture": "Subdomain-based tenant isolation",
    "Learner dashboards that focus attention": "Personalised player dashboard (matches, standings, challenges)",
    "Role-based learning paths": "Role-based access (admin / captain / player)",
    "Adaptive content sequencing": "Rotating match schedule generation",
    "Feedback loops with real assessment": "Score entry, dispute, and confirmation flows",
    "Curriculum roadmap visibility": "Season planner with standings and movement indicators",
}


class TimelineNodeBlock(StructBlock):
    year = CharBlock(
        max_length=20,
        help_text="Year or short label (e.g. '2005' or '2024–25').",
    )
    label = CharBlock(max_length=160, help_text="Short headline for the node.")
    body = RichTextBlock()
    audience_tags = ListBlock(
        ChoiceBlock(choices=AUDIENCE_FOCUS_CHOICES),
        required=False,
        help_text="Audience archetypes for which this node is most relevant. Used by the ?role= adaptation in Phase 2.",
    )

    class Meta:
        icon = "history"
        label = "Timeline node"


class TranslationRowBlock(StructBlock):
    qlubpro_feature = CharBlock(
        max_length=200,
        help_text="QlubPro side of the translation.",
    )
    learning_equivalent = CharBlock(
        max_length=200,
        help_text="Learning-platform equivalent.",
    )
    commentary = RichTextBlock(
        required=False,
        help_text="One short paragraph on why the pattern transfers.",
    )
    screenshot = ImageChooserBlock(
        required=False,
        help_text="Optional QlubPro screenshot shown when the row is expanded.",
    )
    audience_tags = ListBlock(
        ChoiceBlock(choices=AUDIENCE_FOCUS_CHOICES),
        required=False,
        help_text="Audience archetypes for which this row is most relevant. Used by the ?role= adaptation.",
    )

    class Meta:
        icon = "code"
        label = "QlubPro → learning row"


class AICardBlock(StructBlock):
    title = CharBlock(max_length=160)
    summary = RichTextBlock()
    link = URLBlock(required=False)
    link_label = CharBlock(max_length=80, required=False)

    class Meta:
        icon = "snippet"
        label = "AI project card"


class ReflectionBlock(StructBlock):
    prompt = TextBlock(help_text="The reflection question shown to the visitor.")
    options = ListBlock(
        CharBlock(max_length=160),
        help_text="Options the visitor can choose from.",
    )

    class Meta:
        icon = "help"
        label = "Reflection prompt"


class InteractivePage(Page):
    """A single, reusable interactive portfolio page.

    Phase 1 ships the schema and a static template. Phase 2 adds Alpine-driven
    interactivity and ?role= adaptation. Phase 3 wires up the AI chat using the
    chat_system_prompt field.
    """

    max_count = 1

    target_company = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional employer name. Rendered in the closing employer line only when 'Show employer section' is enabled.",
    )
    target_role = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional role title. Rendered in the closing employer line only when 'Show employer section' is enabled.",
    )
    audience_focus = models.CharField(
        max_length=40,
        choices=AUDIENCE_FOCUS_CHOICES,
        default="generic",
        help_text="Default audience archetype when no ?role= query param is supplied.",
    )
    accent_color = models.CharField(
        max_length=7,
        default="#1A3A5C",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Enter a 6-digit hex colour with leading '#', e.g. #1A3A5C.",
            )
        ],
        help_text="Six-digit hex colour driving the page's accent (e.g. #1A3A5C for Geotab). Injected into an inline style block — must be a valid hex value.",
    )
    show_employer_section = models.BooleanField(
        default=False,
        help_text="Show the optional employer-specific section in the closing.",
    )
    chat_enabled = models.BooleanField(
        default=True,
        help_text="Wired up in Phase 3. Disable to hide the chat without removing data.",
    )

    hero_kicker = models.CharField(
        max_length=160,
        blank=True,
        help_text="Small uppercase label above the hero statement.",
    )
    hero_statement = RichTextField(
        blank=True,
        help_text="The full-viewport opening statement.",
    )

    timeline_nodes = StreamField(
        [("timeline_node", TimelineNodeBlock())],
        blank=True,
        use_json_field=True,
    )

    translation_rows = StreamField(
        [("translation_row", TranslationRowBlock())],
        blank=True,
        use_json_field=True,
    )

    ai_cards = StreamField(
        [("ai_card", AICardBlock())],
        blank=True,
        use_json_field=True,
    )

    reflection = StreamField(
        [("reflection", ReflectionBlock())],
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    closing_paragraph = RichTextField(blank=True)

    chat_system_prompt = models.TextField(
        blank=True,
        help_text="System prompt sent to the AI chat. Wired up in Phase 3.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_kicker"),
                FieldPanel("hero_statement"),
            ],
            heading="Hero",
        ),
        FieldPanel("timeline_nodes"),
        FieldPanel("translation_rows"),
        FieldPanel("ai_cards"),
        FieldPanel("reflection"),
        FieldPanel("closing_paragraph"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("target_company"),
                FieldPanel("target_role"),
                FieldPanel("audience_focus"),
                FieldPanel("accent_color"),
                FieldPanel("show_employer_section"),
            ],
            heading="Application context",
        ),
        MultiFieldPanel(
            [
                FieldPanel("chat_enabled"),
                FieldPanel("chat_system_prompt"),
            ],
            heading="AI chat (Phase 3)",
        ),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Interactive page"
        verbose_name_plural = "Interactive pages"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        param = request.GET.get("role", "") if request else ""
        from_url = audience_focus_from_url(param)
        role_explicit = from_url is not None
        focus = from_url or self.audience_focus

        context["audience_focus"] = focus
        context["audience_focus_url"] = audience_focus_to_url(focus)
        context["audience_focus_display"] = dict(AUDIENCE_FOCUS_CHOICES).get(focus, "")
        context["audience_role_explicit"] = role_explicit
        context["timeline_nodes_ordered"] = self._order_blocks_by_audience(self.timeline_nodes, focus)
        context["translation_rows_ordered"] = self._order_blocks_by_audience(self.translation_rows, focus)
        context["reflection_option_echoes"] = self._build_reflection_echoes()
        return context

    def _build_reflection_echoes(self):
        """Pair each authored reflection option with its matching translation row.

        Returns a list of dicts the template iterates over to render hidden
        echo cards — one per option — that reveal inline when the visitor picks
        that option. An option with no mapping (or a mapping that doesn't
        resolve to a known row) is omitted.
        """
        if not self.reflection or not self.translation_rows:
            return []

        rows_by_key = {block.value.get("qlubpro_feature"): block.value for block in self.translation_rows}

        try:
            options = self.reflection[0].value.get("options") or []
        except (IndexError, AttributeError):
            return []

        echoes = []
        for option_text in options:
            row_key = REFLECTION_OPTION_TO_ROW_KEY.get(option_text)
            row = rows_by_key.get(row_key) if row_key else None
            if row is None:
                continue
            echoes.append(
                {
                    "option": option_text,
                    "qlubpro_feature": row.get("qlubpro_feature", ""),
                    "learning_equivalent": row.get("learning_equivalent", ""),
                    "commentary": row.get("commentary"),
                }
            )
        return echoes

    @staticmethod
    def _order_blocks_by_audience(stream, focus):
        """Stable sort: blocks tagged with `focus` come first, then the rest.

        `generic` is treated as 'no preference' — return original order so the
        editor's authored sequence is respected when no role is selected.
        """
        blocks = list(stream)
        if focus == "generic":
            return blocks
        matches = [b for b in blocks if focus in (b.value.get("audience_tags") or [])]
        rest = [b for b in blocks if focus not in (b.value.get("audience_tags") or [])]
        return matches + rest
