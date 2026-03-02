from django import forms
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


@register_snippet
class TechTag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class WorkIndexPage(Page):
    subpage_types = ["work.ProjectPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        domain = request.GET.get("domain", "")
        projects = (
            ProjectPage.objects.child_of(self)
            .live()
            .order_by("-first_published_at")
            .prefetch_related("tech_stack")
        )
        if domain in ("ld", "software", "hybrid"):
            projects = projects.filter(primary_domain=domain)
        context["projects"] = projects
        context["current_domain"] = domain
        return context


class ProjectPage(Page):
    tagline = models.CharField(max_length=250)
    role = models.CharField(max_length=150)
    client_context = models.CharField(max_length=250)

    STATUS_CHOICES = [
        ("production", "Production"),
        ("open_source", "Open Source"),
        ("archived", "Archived"),
    ]
    DOMAIN_CHOICES = [
        ("ld", "L&D"),
        ("software", "Software"),
        ("hybrid", "Hybrid"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    primary_domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    tech_stack = ParentalManyToManyField("work.TechTag", blank=True)
    body = StreamField(
        [
            ("rich_text", RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
    )
    outcome = models.TextField(blank=True)
    link_github = models.URLField(blank=True)
    link_live = models.URLField(blank=True)
    link_pypi = models.URLField(blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("tagline"),
        FieldPanel("role"),
        FieldPanel("client_context"),
        FieldPanel("status"),
        FieldPanel("primary_domain"),
        FieldPanel("tech_stack", widget=forms.CheckboxSelectMultiple),
        FieldPanel("hero_image"),
        FieldPanel("body"),
        FieldPanel("outcome"),
        FieldPanel("link_github"),
        FieldPanel("link_live"),
        FieldPanel("link_pypi"),
        FieldPanel("featured"),
    ]

    parent_page_types = ["work.WorkIndexPage"]
