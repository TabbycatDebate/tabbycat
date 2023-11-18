from django.utils.text import slugify

from utils.management.base import TournamentCommand

from ...presets import all_presets, get_preset_from_slug


class Command(TournamentCommand):

    help = "Applies a preferences preset"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("preset", choices=[slugify(x.__name__) for x in all_presets()])

    def handle_tournament(self, tournament, **options):
        selected_preset = get_preset_from_slug(options["preset"])
        self.stdout.write("Applying preset: " + selected_preset.name)
        selected_preset.save(tournament)
