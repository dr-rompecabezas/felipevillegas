from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, Site

from contact.models import ContactPage
from home.models import HomePage
from interactive.models import (
    REFLECTION_OPTION_TO_ROW_KEY,
    InteractivePage,
    audience_focus_from_url,
    audience_focus_to_url,
)
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

    def test_accent_color_rejects_invalid_hex(self):
        # Validate the field's validators directly — sidesteps treebeard's path/depth
        # requirements that come with full_clean()/clean_fields() on a Page subclass.
        field = InteractivePage._meta.get_field("accent_color")
        with self.assertRaises(ValidationError):
            for validator in field.validators:
                validator("not-hx")

    def test_accent_color_accepts_valid_hex(self):
        field = InteractivePage._meta.get_field("accent_color")
        for validator in field.validators:
            validator("#C4622D")  # should not raise


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


class AudienceFocusUrlHelpersTests(TestCase):
    """Pure helper tests — no DB or page tree needed."""

    def test_to_url_swaps_underscores_for_dashes(self):
        self.assertEqual(audience_focus_to_url("program_designer"), "program-designer")
        self.assertEqual(audience_focus_to_url("generic"), "generic")

    def test_from_url_known_slugs(self):
        self.assertEqual(audience_focus_from_url("program-designer"), "program_designer")
        self.assertEqual(audience_focus_from_url("lms-architect"), "lms_architect")
        self.assertEqual(audience_focus_from_url("learning-engineer"), "learning_engineer")
        self.assertEqual(audience_focus_from_url("technical-id"), "technical_id")
        self.assertEqual(audience_focus_from_url("generic"), "generic")

    def test_from_url_accepts_underscored_form(self):
        self.assertEqual(audience_focus_from_url("program_designer"), "program_designer")

    def test_from_url_is_case_insensitive_and_strips(self):
        self.assertEqual(audience_focus_from_url("  Program-Designer "), "program_designer")

    def test_from_url_unknown_returns_none(self):
        self.assertIsNone(audience_focus_from_url("ceo"))
        self.assertIsNone(audience_focus_from_url("not-a-role"))

    def test_from_url_empty_returns_none(self):
        self.assertIsNone(audience_focus_from_url(""))
        self.assertIsNone(audience_focus_from_url("   "))


class RoleAdaptationTests(InteractivePageTestCase):
    def setUp(self):
        super().setUp()
        call_command("populate_interactive_page")

    def test_no_role_param_falls_back_to_page_default(self):
        # Page default is 'generic' from populate_interactive_page.
        response = self.client.get("/interactive/")
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["audience_focus"], "generic")
        self.assertFalse(ctx["audience_role_explicit"])
        self.assertEqual(ctx["audience_focus_url"], "generic")

    def test_known_role_slug_overrides_default(self):
        response = self.client.get("/interactive/?role=program-designer")
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["audience_focus"], "program_designer")
        self.assertTrue(ctx["audience_role_explicit"])
        self.assertEqual(ctx["audience_focus_url"], "program-designer")
        self.assertEqual(ctx["audience_focus_display"], "Program Experience Designer")

    def test_unknown_role_falls_back_to_page_default(self):
        response = self.client.get("/interactive/?role=ceo")
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["audience_focus"], "generic")
        self.assertFalse(ctx["audience_role_explicit"])

    def test_empty_role_falls_back_to_page_default(self):
        response = self.client.get("/interactive/?role=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["audience_focus"], "generic")
        self.assertFalse(response.context["audience_role_explicit"])

    def test_explicit_generic_is_recognised(self):
        response = self.client.get("/interactive/?role=generic")
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["audience_focus"], "generic")
        # generic IS a valid choice, so the role IS explicit
        self.assertTrue(ctx["audience_role_explicit"])

    def test_all_acceptance_criteria_urls_render(self):
        # Acceptance: each of these URLs must render without error.
        for slug in [
            "program-designer",
            "lms-architect",
            "learning-engineer",
            "technical-id",
            "generic",
        ]:
            with self.subTest(slug=slug):
                response = self.client.get(f"/interactive/?role={slug}")
                self.assertEqual(response.status_code, 200)

    def test_role_kicker_renders_only_when_explicit(self):
        # No role param: the "For <role>" pill element must not appear.
        # (The .role-kicker CSS rule is always in the inline <style>; we look
        # for the rendered <p class="role-kicker"> element instead.)
        response = self.client.get("/interactive/")
        self.assertNotIn('<p class="role-kicker', response.content.decode("utf-8"))

        # With a known role: the pill renders with the display name.
        response = self.client.get("/interactive/?role=program-designer")
        body = response.content.decode("utf-8")
        self.assertIn('<p class="role-kicker', body)
        self.assertIn("Program Experience Designer", body)

    def test_timeline_ordering_puts_matching_nodes_first(self):
        response = self.client.get("/interactive/?role=learning-engineer")
        ordered = response.context["timeline_nodes_ordered"]

        # Every node tagged with learning_engineer must precede the first untagged one.
        seen_unmatched = False
        for block in ordered:
            tags = block.value.get("audience_tags") or []
            if "learning_engineer" in tags:
                self.assertFalse(
                    seen_unmatched,
                    "A learning_engineer-tagged node appeared after an untagged node — ordering broken.",
                )
            else:
                seen_unmatched = True

    def test_translation_ordering_puts_matching_rows_first(self):
        response = self.client.get("/interactive/?role=lms-architect")
        ordered = response.context["translation_rows_ordered"]

        seen_unmatched = False
        for block in ordered:
            tags = block.value.get("audience_tags") or []
            if "lms_architect" in tags:
                self.assertFalse(
                    seen_unmatched,
                    "An lms_architect-tagged row appeared after an untagged row — ordering broken.",
                )
            else:
                seen_unmatched = True

    def test_generic_preserves_authored_order(self):
        response_generic = self.client.get("/interactive/?role=generic")
        response_default = self.client.get("/interactive/")

        # Both produce the same ordering as the authored stream.
        authored_years = [b.value["year"] for b in InteractivePage.objects.first().timeline_nodes]
        generic_years = [b.value["year"] for b in response_generic.context["timeline_nodes_ordered"]]
        default_years = [b.value["year"] for b in response_default.context["timeline_nodes_ordered"]]
        self.assertEqual(generic_years, authored_years)
        self.assertEqual(default_years, authored_years)

    def test_alpine_static_asset_referenced(self):
        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        # The vendored Alpine asset is referenced (not the CDN).
        self.assertIn("alpine.min.js", body)
        self.assertNotIn("cdn.jsdelivr.net/npm/alpinejs", body)


class ReflectionEchoTests(InteractivePageTestCase):
    """The reflection echo card surfaces the matching translation row inline.

    These guard the editorial pairing in REFLECTION_OPTION_TO_ROW_KEY, the
    context plumbing in get_context, and the rendered echo elements.
    """

    def setUp(self):
        super().setUp()
        call_command("populate_interactive_page")

    def test_each_mapped_option_resolves_to_a_real_row(self):
        page = InteractivePage.objects.first()
        row_keys = {b.value.get("qlubpro_feature") for b in page.translation_rows}
        for option, row_key in REFLECTION_OPTION_TO_ROW_KEY.items():
            with self.subTest(option=option):
                self.assertIn(
                    row_key,
                    row_keys,
                    f"Reflection option '{option}' is paired with row "
                    f"'{row_key}' which does not exist in translation_rows. "
                    "Update REFLECTION_OPTION_TO_ROW_KEY.",
                )

    def test_each_authored_option_has_an_echo(self):
        # Every option the visitor can click should produce an echo card.
        page = InteractivePage.objects.first()
        options = page.reflection[0].value["options"]
        response = self.client.get("/interactive/")
        echoes = response.context["reflection_option_echoes"]
        echoed_options = {e["option"] for e in echoes}
        for option in options:
            with self.subTest(option=option):
                self.assertIn(option, echoed_options)

    def test_echo_carries_paired_row_content(self):
        response = self.client.get("/interactive/")
        echoes = {e["option"]: e for e in response.context["reflection_option_echoes"]}
        sample = echoes["Multi-tenant LMS architecture"]
        self.assertEqual(sample["qlubpro_feature"], "Subdomain-based tenant isolation")
        self.assertEqual(sample["learning_equivalent"], "Multi-org LMS architecture")
        self.assertIn("ContextVar", str(sample["commentary"]))

    def test_echoes_render_in_html(self):
        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        # The page wires alpine echo cards keyed on reflectionChoice.
        self.assertIn("reflectionChoice ===", body)
        # An echo card carries the paired QlubPro feature text in the DOM
        # so the visitor sees both sides of the translation when they pick
        # a reflection option.
        self.assertIn("Subdomain-based tenant isolation", body)  # row 1 qlubpro side
        self.assertIn("Score entry, dispute, and confirmation flows", body)  # row 6
        # The "Jump to Module Two" affordance is present.
        self.assertIn("See in Module Two", body)
        # Old broken behaviour must be gone.
        self.assertNotIn("is-reflection-match", body)
        self.assertNotIn("isReflectionMatch", body)
