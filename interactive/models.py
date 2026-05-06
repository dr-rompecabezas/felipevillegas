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
        help_text="Optional employer name. Used in closing paragraph and the optional employer section.",
    )
    target_role = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional role title. Used in closing paragraph.",
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
        help_text="Hex colour driving the page's accent (e.g. #1A3A5C for Geotab).",
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
        context["audience_focus"] = self.audience_focus
        return context
