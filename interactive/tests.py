import json
from types import SimpleNamespace
from unittest.mock import patch

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
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

    def test_explicit_generic_is_recognised_but_not_emphasised(self):
        # generic is a known choice → audience_role_explicit stays True for
        # observability. But emphasis (dimming, role pill) must stay OFF —
        # otherwise the visitor sees every block dimmed for a "no preference"
        # archetype.
        response = self.client.get("/interactive/?role=generic")
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["audience_focus"], "generic")
        self.assertTrue(ctx["audience_role_explicit"])
        self.assertFalse(ctx["audience_emphasis_active"])

        body = response.content.decode("utf-8")
        # No dimming attribute, no role pill on the page.
        self.assertIn('data-emphasis-active="false"', body)
        self.assertNotIn('<p class="role-kicker', body)

    def test_emphasis_active_for_non_generic_role(self):
        response = self.client.get("/interactive/?role=program-designer")
        self.assertTrue(response.context["audience_emphasis_active"])
        body = response.content.decode("utf-8")
        self.assertIn('data-emphasis-active="true"', body)

    def test_emphasis_inactive_when_no_role_param(self):
        response = self.client.get("/interactive/")
        self.assertFalse(response.context["audience_emphasis_active"])
        body = response.content.decode("utf-8")
        self.assertIn('data-emphasis-active="false"', body)

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

    def test_timeline_preserves_chronological_order_across_roles(self):
        # Timelines are chronological narratives; reordering by audience tag
        # breaks the arc. Authored order must be preserved regardless of role.
        authored_years = [b.value["year"] for b in InteractivePage.objects.first().timeline_nodes]
        for slug in ["learning-engineer", "lms-architect", "program-designer", "technical-id"]:
            with self.subTest(role=slug):
                response = self.client.get(f"/interactive/?role={slug}")
                rendered_years = [b.value["year"] for b in response.context["timeline_nodes_ordered"]]
                self.assertEqual(rendered_years, authored_years)

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


class TranslationRowBackfillTests(InteractivePageTestCase):
    """Validate the data-migration logic that backfills audience_tags on
    translation rows that pre-date the audience_tags field.

    The migration itself runs once at deploy time, so we can't easily replay
    it inside a test transaction. Instead we exercise the migration's pure
    helpers against simulated stale and partially-migrated data.
    """

    @staticmethod
    def _migration_module():
        import importlib  # noqa: PLC0415

        return importlib.import_module("interactive.migrations.0004_backfill_translation_row_audience_tags")

    def test_helper_adds_missing_tags_and_leaves_present_ones(self):
        patch = self._migration_module()._patch_blocks

        blocks = [
            {
                "type": "translation_row",
                "value": {
                    "qlubpro_feature": "Subdomain-based tenant isolation",
                    "learning_equivalent": "Multi-org LMS architecture",
                    "audience_tags": [],  # stale, empty list
                },
            },
            {
                "type": "translation_row",
                "value": {
                    "qlubpro_feature": "Rotating match schedule generation",
                    "learning_equivalent": "Adaptive content sequencing",
                    "audience_tags": ["program_designer"],  # already present, untouched
                },
            },
            {
                "type": "translation_row",
                "value": {
                    "qlubpro_feature": "An unmapped feature",
                    "learning_equivalent": "Something",
                },
            },
        ]
        changed = patch(blocks)
        self.assertTrue(changed)
        self.assertEqual(
            blocks[0]["value"]["audience_tags"],
            ["lms_architect", "learning_engineer"],
        )
        self.assertEqual(
            blocks[1]["value"]["audience_tags"],
            ["program_designer"],
        )
        self.assertNotIn("audience_tags", blocks[2]["value"])

    def test_helper_is_noop_when_all_blocks_already_tagged(self):
        patch = self._migration_module()._patch_blocks
        blocks = [
            {
                "type": "translation_row",
                "value": {
                    "qlubpro_feature": "Subdomain-based tenant isolation",
                    "audience_tags": ["lms_architect"],
                },
            },
        ]
        self.assertFalse(patch(blocks))


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


def _fake_anthropic_response(reply: str = "Hello.", input_tokens: int = 50, output_tokens: int = 25):
    """Build a minimal duck-typed Anthropic Messages response."""
    return SimpleNamespace(
        content=[SimpleNamespace(text=reply, type="text")],
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


@override_settings(
    ANTHROPIC_API_KEY="test-key",
    CHAT_DAILY_INPUT_TOKEN_BUDGET=200,
    CHAT_DAILY_OUTPUT_TOKEN_BUDGET=100,
    CHAT_RPM=3,
    CHAT_INPUT_MAX_CHARS=120,
    CHAT_MAX_OUTPUT_TOKENS=50,
)
class ChatViewTests(InteractivePageTestCase):
    """Tests for the /api/interactive/chat/ proxy view."""

    def setUp(self):
        super().setUp()
        # CSRF cookie is needed for the enforce_csrf_checks=True client.
        self.client = Client(enforce_csrf_checks=True)
        self.page = InteractivePage(
            title="Interactive",
            slug="interactive",
            live=True,
            chat_enabled=True,
            chat_system_prompt="You are a test assistant.",
        )
        self.home.add_child(instance=self.page)
        cache.clear()

    def _post(self, payload, *, with_csrf: bool = True, ip: str = "10.0.0.1"):
        url = reverse("interactive:chat")
        headers = {"REMOTE_ADDR": ip, "content_type": "application/json"}
        if with_csrf:
            # The page now renders {% csrf_token %} inside the chat form, so
            # the GET response sets the csrftoken cookie naturally — no manual
            # cookie injection required.
            self.client.get("/interactive/", REMOTE_ADDR=ip)
            cookie = self.client.cookies.get("csrftoken")
            self.assertIsNotNone(cookie, "GET to /interactive/ must seed csrftoken cookie")
            headers["HTTP_X_CSRFTOKEN"] = cookie.value
        return self.client.post(url, data=json.dumps(payload), **headers)

    def test_csrf_rejects_request_without_token(self):
        url = reverse("interactive:chat")
        response = self.client.post(
            url,
            data=json.dumps({"message": "Hi"}),
            content_type="application/json",
            REMOTE_ADDR="10.0.0.99",
        )
        self.assertEqual(response.status_code, 403)

    def test_input_length_cap_rejects_oversized_message(self):
        long_msg = "x" * 121  # CHAT_INPUT_MAX_CHARS = 120
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            response = self._post({"message": long_msg})
        self.assertEqual(response.status_code, 413)
        body = response.json()
        self.assertEqual(body["error"], "input_too_long")
        self.assertEqual(body["limit"], 120)
        client_cls.assert_not_called()

    def test_json_response_shape_on_success(self):
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            client_cls.return_value.messages.create.return_value = _fake_anthropic_response(
                reply="The architecture transfers.",
                input_tokens=42,
                output_tokens=17,
            )
            response = self._post({"message": "Tell me about Felipe."})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), {"reply", "input_tokens", "output_tokens"})
        self.assertEqual(body["reply"], "The architecture transfers.")
        self.assertEqual(body["input_tokens"], 42)
        self.assertEqual(body["output_tokens"], 17)

    def test_system_prompt_combines_page_and_profile_with_cache_control(self):
        # Anthropic gets a single cache-marked system block whose text contains
        # both the editable page prompt (style/scope) and the version-controlled
        # profile (facts). Caching is what makes the long profile affordable —
        # this test pins that the cache_control marker is set.
        from interactive.views import _PROFILE_TEXT  # noqa: PLC0415

        self.assertTrue(_PROFILE_TEXT, "profile.md must load at import time")
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            client_cls.return_value.messages.create.return_value = _fake_anthropic_response()
            self._post({"message": "Hi"})
        call_kwargs = client_cls.return_value.messages.create.call_args.kwargs
        system = call_kwargs["system"]
        self.assertIsInstance(system, list)
        self.assertEqual(len(system), 1)
        block = system[0]
        self.assertEqual(block["type"], "text")
        self.assertEqual(block["cache_control"], {"type": "ephemeral"})
        self.assertIn("test assistant", block["text"])  # page prompt portion
        # Profile sentinel: a stable phrase from interactive/data/profile.md.
        self.assertIn("Felipe Villegas", block["text"])

    def test_rpm_throttle_returns_documented_shape(self):
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            client_cls.return_value.messages.create.return_value = _fake_anthropic_response()
            for _ in range(3):  # CHAT_RPM = 3
                ok = self._post({"message": "Hi"})
                self.assertEqual(ok.status_code, 200)
            blocked = self._post({"message": "Hi"})
        self.assertEqual(blocked.status_code, 429)
        body = blocked.json()
        self.assertEqual(body["error"], "rate_limited")
        self.assertIn("retry_after", body)

    def test_daily_budget_exhaustion_returns_documented_shape(self):
        # Output budget is 100 tokens; one call burns 60 → second call still
        # allowed; second burns 60 → cumulative 120 > 100, third call blocked.
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            client_cls.return_value.messages.create.return_value = _fake_anthropic_response(
                output_tokens=60, input_tokens=10
            )
            r1 = self._post({"message": "one"})
            r2 = self._post({"message": "two"})
            blocked = self._post({"message": "three"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(blocked.status_code, 429)
        body = blocked.json()
        self.assertEqual(body["error"], "budget_exhausted")
        self.assertIn("contact_email", body)

    def test_chat_disabled_when_flag_off(self):
        from django.middleware.csrf import get_token

        self.page.chat_enabled = False
        self.page.save_revision().publish()
        # The form (and its {% csrf_token %}) doesn't render when disabled,
        # so seed a valid token directly to get past CSRF middleware and
        # actually reach the view's chat_enabled check.
        request = self.client.get("/interactive/").wsgi_request
        token = get_token(request)
        self.client.cookies["csrftoken"] = token
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            response = self.client.post(
                reverse("interactive:chat"),
                data=json.dumps({"message": "Hi"}),
                content_type="application/json",
                headers={"x-csrftoken": token},
                REMOTE_ADDR="10.0.0.1",
            )
        self.assertEqual(response.status_code, 404)
        client_cls.assert_not_called()

    def test_chat_disabled_hides_panel_in_html(self):
        self.page.chat_enabled = False
        self.page.save_revision().publish()
        response = self.client.get("/interactive/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        # The chat module heading and the form markup must be absent.
        self.assertNotIn("Module Four", body)
        self.assertNotIn('class="chat-form"', body)
        # Alpine wiring is also gated — the section's x-data attr must be absent.
        self.assertNotIn('x-data="interactiveChat(', body)

    def test_chat_panel_renders_when_enabled(self):
        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        self.assertIn("Module Four", body)
        self.assertIn('class="chat-form"', body)
        self.assertIn("Single-turn", body)
        # Form posts to the chat endpoint
        self.assertIn(reverse("interactive:chat"), body)


@override_settings(ANTHROPIC_API_KEY="test-key")
class ChatStartersTests(InteractivePageTestCase):
    def test_starters_render_when_seeded(self):
        call_command("populate_interactive_page")
        response = self.client.get("/interactive/")
        body = response.content.decode("utf-8")
        # At least one of the seeded starter questions should appear as a chip.
        self.assertIn('class="chat-starter"', body)
        self.assertIn("How does QlubPro", body)


class ClientIpResolutionTests(TestCase):
    """`_client_ip` must not let a forged X-Forwarded-For value spoof the IP
    used for rate-limit and budget keys. With CHAT_TRUSTED_PROXY_COUNT=N, the
    Nth-from-the-right entry is taken — anything to the left is untrusted.
    """

    @staticmethod
    def _request(xff: str | None, remote_addr: str = "10.0.0.1"):
        from django.test import RequestFactory

        rf = RequestFactory()
        headers = {"REMOTE_ADDR": remote_addr}
        if xff is not None:
            headers["HTTP_X_FORWARDED_FOR"] = xff
        return rf.get("/api/interactive/chat/", **headers)

    @override_settings(CHAT_TRUSTED_PROXY_COUNT=1)
    def test_single_proxy_returns_rightmost_xff(self):
        from interactive.views import _client_ip

        # Attacker-supplied "1.2.3.4" on the left, real client "9.9.9.9" appended
        # by the trusted proxy on the right.
        req = self._request(xff="1.2.3.4, 9.9.9.9")
        self.assertEqual(_client_ip(req), "9.9.9.9")

    @override_settings(CHAT_TRUSTED_PROXY_COUNT=1)
    def test_falls_back_to_remote_addr_when_no_xff(self):
        from interactive.views import _client_ip

        req = self._request(xff=None, remote_addr="10.0.0.7")
        self.assertEqual(_client_ip(req), "10.0.0.7")

    @override_settings(CHAT_TRUSTED_PROXY_COUNT=2)
    def test_two_proxies_skips_one_more_from_the_right(self):
        from interactive.views import _client_ip

        # XFF: client, proxy1, proxy2 → with two trusted hops, the client is
        # the second entry.
        req = self._request(xff="9.9.9.9, 10.0.0.1, 10.0.0.2")
        self.assertEqual(_client_ip(req), "10.0.0.1")


@override_settings(
    ANTHROPIC_API_KEY="test-key",
    CHAT_DAILY_INPUT_TOKEN_BUDGET=200,
    CHAT_DAILY_OUTPUT_TOKEN_BUDGET=100,
    CHAT_RPM=2,
    CHAT_INPUT_MAX_CHARS=120,
    CHAT_MAX_OUTPUT_TOKENS=50,
)
class ChatRateLimitRecoverableTests(InteractivePageTestCase):
    """The frontend must keep the widget open on RPM throttles and only close
    on permanent stops. The contract is the `error` field on the response, so
    we pin its value here.
    """

    def setUp(self):
        super().setUp()
        self.client = Client(enforce_csrf_checks=True)
        page = InteractivePage(
            title="Interactive",
            slug="interactive",
            live=True,
            chat_enabled=True,
            chat_system_prompt="You are a test assistant.",
        )
        self.home.add_child(instance=page)
        cache.clear()

    def test_rate_limited_error_string_is_distinct_from_budget(self):
        url = reverse("interactive:chat")
        self.client.get("/interactive/", REMOTE_ADDR="10.0.0.42")
        token = self.client.cookies.get("csrftoken").value
        with patch("interactive.views.anthropic.Anthropic") as client_cls:
            client_cls.return_value.messages.create.return_value = _fake_anthropic_response()
            for _ in range(2):  # CHAT_RPM=2
                self.client.post(
                    url,
                    data=json.dumps({"message": "Hi"}),
                    content_type="application/json",
                    headers={"x-csrftoken": token},
                    REMOTE_ADDR="10.0.0.42",
                )
            blocked = self.client.post(
                url,
                data=json.dumps({"message": "Hi"}),
                content_type="application/json",
                headers={"x-csrftoken": token},
                REMOTE_ADDR="10.0.0.42",
            )
        self.assertEqual(blocked.status_code, 429)
        body = blocked.json()
        # The frontend keys "permanent close" off `error` — `rate_limited`
        # must stay distinct from `budget_exhausted` so transient throttles
        # don't lock users out until reload.
        self.assertEqual(body["error"], "rate_limited")
        self.assertNotEqual(body["error"], "budget_exhausted")
