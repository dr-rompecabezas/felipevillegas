from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class PhotographyIndexPage(Page):
    subpage_types = ["photography.GalleryPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["galleries"] = GalleryPage.objects.child_of(self).live().order_by("-first_published_at")
        return context


class GalleryPage(Page):
    CATEGORY_CHOICES = [
        ("landscape", "Landscape"),
        ("wildlife", "Wildlife"),
        ("urban", "Urban"),
        ("event", "Event"),
        ("other", "Other"),
    ]

    description = models.TextField(blank=True)
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    images = StreamField(
        [("image", ImageChooserBlock())],
        blank=True,
    )
    is_client_gallery = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("cover_image"),
        FieldPanel("category"),
        FieldPanel("images"),
        FieldPanel("is_client_gallery"),
    ]

    parent_page_types = ["photography.PhotographyIndexPage"]
