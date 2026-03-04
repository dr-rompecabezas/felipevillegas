from wagtail.admin.panels import FieldPanel
from wagtail.blocks import (
    CharBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
    TextBlock,
)
from wagtail.fields import StreamField
from wagtail.models import Page


class CTABlock(StructBlock):
    text = CharBlock()
    url = CharBlock()

    class Meta:
        icon = "link"


class HeroBlock(StructBlock):
    heading = CharBlock()
    subtitle = TextBlock()
    cta_primary = CTABlock()
    cta_secondary = CTABlock()

    class Meta:
        icon = "title"
        label = "Hero"


class AboutBlock(StructBlock):
    content = RichTextBlock()

    class Meta:
        icon = "user"
        label = "About"


class FeaturedWorkBlock(StructBlock):
    heading = CharBlock(default="Selected Work")

    class Meta:
        icon = "folder-open-inverse"
        label = "Featured Work"


class SkillsBlock(StructBlock):
    heading = CharBlock()
    skills = ListBlock(CharBlock())

    class Meta:
        icon = "list-ul"
        label = "Skills"


class ContactCTABlock(StructBlock):
    heading = CharBlock()
    message = TextBlock()

    class Meta:
        icon = "mail"
        label = "Contact CTA"


class HomePage(Page):
    body = StreamField(
        [
            ("hero", HeroBlock()),
            ("about", AboutBlock()),
            ("featured_work", FeaturedWorkBlock()),
            ("skills", SkillsBlock()),
            ("contact_cta", ContactCTABlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from work.models import ProjectPage

        context["featured_projects"] = ProjectPage.objects.live().filter(featured=True).select_related("hero_image")[:6]
        return context
