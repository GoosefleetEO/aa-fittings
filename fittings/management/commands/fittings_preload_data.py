from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Preloads common ship and module types from ESI."

    def handle(self, *args, **kwargs):
        call_command(
            "eveuniverse_load_types",
            "Fittings",
            "--category_id_with_dogma",
            "8",
            "--category_id_with_dogma",
            "7",
            "--category_id_with_dogma",
            "6",
            "--category_id_with_dogma",
            "18",
            "--category_id_with_dogma",
            "20",
            "--category_id_with_dogma",
            "22",
            "--category_id_with_dogma",
            "87"
        )
