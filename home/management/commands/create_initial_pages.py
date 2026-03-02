from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from contact.models import ContactPage
from home.models import HomePage
from photography.models import PhotographyIndexPage
from work.models import WorkIndexPage


class Command(BaseCommand):
    help = "Create the initial Wagtail page tree and set the default site root."

    def handle(self, *args, **options):
        # Wagtail ships with a default root page (pk=1) and a "Welcome to Wagtail" page.
        # We build our tree under the true root (depth=1).
        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("No root page found — run migrate first.")
            return

        if HomePage.objects.exists():
            self.stdout.write("Page tree already exists, skipping.")
            return

        # Remove the default "Welcome to your new Wagtail site!" page if present.
        for page in Page.objects.filter(depth=2):
            page.delete()

        # Re-fetch root so treebeard's numchild is accurate after deletion.
        root = Page.objects.get(pk=root.pk)

        # 1. HomePage
        home = HomePage(
            title="Felipe Villegas",
            slug="home",
            live=True,
        )
        root.add_child(instance=home)
        self.stdout.write(f"  Created HomePage: '{home.title}' (slug: {home.slug})")

        # 2. Child index pages
        work_index = WorkIndexPage(title="Work", slug="work", live=True)
        home.add_child(instance=work_index)
        self.stdout.write(f"  Created WorkIndexPage: '{work_index.title}'")

        photo_index = PhotographyIndexPage(title="Photography", slug="photography", live=True)
        home.add_child(instance=photo_index)
        self.stdout.write(f"  Created PhotographyIndexPage: '{photo_index.title}'")

        contact = ContactPage(title="Contact", slug="contact", live=True)
        home.add_child(instance=contact)
        self.stdout.write(f"  Created ContactPage: '{contact.title}'")

        # 3. Point the default Site at HomePage
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = home
            site.site_name = "Felipe Villegas"
            site.save()
            self.stdout.write(f"  Updated Site '{site.site_name}' → root: '{home.title}'")
        else:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                root_page=home,
                site_name="Felipe Villegas",
                is_default_site=True,
            )
            self.stdout.write("  Created default Site pointing to HomePage")

        # Fix any treebeard numchild inconsistencies left by deletions or add_child calls.
        from django.core.management import call_command

        call_command("fixtree", verbosity=0)

        self.stdout.write(self.style.SUCCESS("Done. Page tree is ready."))
