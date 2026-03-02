from wagtail.models import Page


class ContactPage(Page):
    content_panels = Page.content_panels

    parent_page_types = ["wagtailcore.Page"]
