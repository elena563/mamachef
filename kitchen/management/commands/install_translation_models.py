from argostranslate import package, settings
from django.core.management.base import BaseCommand

LANGUAGE_PAIRS = (("it", "en"), ("en", "it"))


class Command(BaseCommand):
    help = "Install the Argos Translate models needed for Italian/English translations."

    def handle(self, *args, **options):
        package.update_package_index()
        if not settings.local_package_index.exists():
            self.stderr.write("Could not download the Argos package index.")
            return

        installed = {
            (pkg.from_code, pkg.to_code) for pkg in package.get_installed_packages() if pkg.type == "translate"
        }
        available = package.get_available_packages()

        for from_code, to_code in LANGUAGE_PAIRS:
            if (from_code, to_code) in installed:
                self.stdout.write(f"{from_code}->{to_code} already installed")
                continue

            match = next(
                (pkg for pkg in available if pkg.from_code == from_code and pkg.to_code == to_code),
                None,
            )
            if match is None:
                self.stderr.write(f"No package available for {from_code}->{to_code}")
                continue

            match.install()
            self.stdout.write(self.style.SUCCESS(f"Installed {from_code}->{to_code}"))
