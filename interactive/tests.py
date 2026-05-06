from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, Site

from contact.models import ContactPage
from home.models import HomePage
from interactive.models import InteractivePage
from photography.models import PhotographyIndexPage
from work.models import WorkIndexPage


class InteractivePageTestCase(TestCase):
    """Set up a fresh Wagtail page tree before each test."""

    @classmethod
    def setUpTestData(cls):
        # Wagtail seeds a default root page (depth=1) and a "Welcome" page (depth=2)
        # via the wagtailcore migrations. Replace the depth=2 page with our HomePage.
        for page in Page.objects.filter(depth=2):
            page.delete()

        root = Page.objects.get(depth=1)

        cls.home = HomePage(title="Felipe Villegas", slug="home", live=True)
        root.add_child(instance=cls.home)

        cls.work_index = WorkIndexPage(title="Work", slug="work", live=True)
        cls.home.add_child(instance=cls.work_index)

        cls.photography_index = PhotographyIndexPage(title="Photography", slug="photography", live=True)
        cls.home.add_child(instance=cls.photography_index)

        cls.contact = ContactPage(title="Contact", slug="contact", live=True)
        cls.home.add_child(instance=cls.contact)

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = cls.home
            site.save()
        else:
            Site.objects.create(
                hostname="localhost",
                port=80,
                root_page=cls.home,
                site_name="Felipe Villegas",
                is_default_site=True,
            )


class InteractivePageModelTests(InteractivePageTestCase):
    def test_only_creatable_under_homepage(self):
        # Allowed: child of HomePage
        self.assertIn("home.HomePage", InteractivePage.parent_page_types)

        # No subpages permitted
        self.assertEqual(InteractivePage.subpage_types, [])

    def test_max_count_enforced(self):
        page = InteractivePage(title="Interactive", slug="interactive", live=True)
        self.home.add_child(instance=page)
        self.assertEqual(InteractivePage.objects.count(), 1)

        # Wagtail's max_count is enforced in the admin; the class attribute is the
        # source of truth. Verify it's set so admin enforcement is in effect.
        self.assertEqual(InteractivePage.max_count, 1)

    def test_get_context_exposes_audience_focus(self):
        page = InteractivePage(
            title="Interactive",
            slug="interactive",
            live=True,
            audience_focus="program_designer",
        )
        self.home.add_child(instance=page)

        request = self.client.get("/interactive/").wsgi_request
        context = page.get_context(request)
        self.assertEqual(context["audience_focus"], "program_designer")

    def test_default_field_values(self):
        page = InteractivePage(title="Interactive", slug="interactive", live=True)
        self.home.add_child(instance=page)
        self.assertEqual(page.audience_focus, "generic")
        self.assertEqual(page.accent_color, "#1A3A5C")
        self.assertFalse(page.show_employer_section)
        self.assertTrue(page.chat_enabled)


class PopulateInteractivePageCommandTests(InteractivePageTestCase):
    def test_creates_page_when_absent(self):
        self.assertEqual(InteractivePage.objects.count(), 0)
        call_command("populate_interactive_page")
        self.assertEqual(InteractivePage.objects.count(), 1)

        page = InteractivePage.objects.first()
        self.assertEqual(page.slug, "interactive")
        self.assertTrue(page.live)
        self.assertTrue(page.hero_kicker)
        self.assertTrue(page.hero_statement)
        self.assertTrue(page.chat_system_prompt)

    def test_idempotent_without_force(self):
        call_command("populate_interactive_page")
        page = InteractivePage.objects.first()
        original_kicker = page.hero_kicker

        # Mutate to detect whether a second run touches the data.
        page.hero_kicker = "manually edited"
        page.save_revision().publish()

        call_command("populate_interactive_page")
        page.refresh_from_db()
        self.assertEqual(page.hero_kicker, "manually edited")
        # Defensive: confirm the original constant is non-empty for the next test.
        self.assertNotEqual(original_kicker, "")

    def test_force_overwrites(self):
        call_command("populate_interactive_page")
        page = InteractivePage.objects.first()
        page.hero_kicker = "manually edited"
        page.save_revision().publish()

        call_command("populate_interactive_page", "--force")
        page.refresh_from_db()
        self.assertNotEqual(page.hero_kicker, "manually edited")

    def test_streamfields_populate(self):
        call_command("populate_interactive_page")
        page = InteractivePage.objects.first()
        self.assertGreaterEqual(len(page.timeline_nodes), 9)
        self.assertGreaterEqual(len(page.translation_rows), 8)
        self.assertGreaterEqual(len(page.ai_cards), 3)
        self.assertEqual(len(page.reflection), 1)


class InteractivePageRenderTests(InteractivePageTestCase):
    def test_page_renders_after_seeding(self):
        call_command("populate_interactive_page")
        response = self.client.get("/interactive/")
        self.assertEqual(response.status_code, 200)

        body = response.content.decode("utf-8")
        # Hero
        self.assertIn("Portfolio", body)
        # Timeline node sample
        self.assertIn("First e-learning platform", body)
        # Translation row sample
        self.assertIn("Subdomain-based tenant isolation", body)
        # AI card sample
        self.assertIn("CTCMPAO", body)
        # Reflection
        self.assertIn("Multi-tenant LMS architecture", body)
        # Closing
        self.assertIn("f.villegas@thinkelearn.com", body)
        # Accent variable injected
        self.assertIn("--page-accent: #1A3A5C", body)

    def test_employer_section_hidden_by_default(self):
        call_command("populate_interactive_page")
        page = InteractivePage.objects.first()
        page.target_company = "Acme Corp"
        page.target_role = "Program Experience Designer"
        page.save_revision().publish()

        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        # show_employer_section is False by default — employer line must be absent.
        self.assertNotIn("Acme Corp", body)

    def test_employer_section_renders_when_enabled(self):
        call_command("populate_interactive_page")
        page = InteractivePage.objects.first()
        page.target_company = "Acme Corp"
        page.target_role = "Program Experience Designer"
        page.show_employer_section = True
        page.save_revision().publish()

        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        self.assertIn("Acme Corp", body)
        self.assertIn("Program Experience Designer", body)
