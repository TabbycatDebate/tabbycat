from django.core.management.base import CommandError
from django.utils.text import slugify

from utils.management.base import TournamentCommand

from ...presets import all_presets, get_preferences_data


class Command(TournamentCommand):

    help = "Applies a preferences preset"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("preset")

    def handle_tournament(self, tournament, **options):
        preset_name = options["preset"]

        selected_presets = [x for x in all_presets() if slugify(x.__name__) == preset_name]
        if len(selected_presets) == 0:
            self.stdout.write("Hint: Try one of")
            for preset in all_presets():
                self.stdout.write(" - " + slugify(preset.__name__))
            raise CommandError("Could not find preset: " + preset_name)
        elif len(selected_presets) > 1:
            raise CommandError("Found more than one preset for: " + preset_name)

        selected_preset = selected_presets[0]
        self.stdout.write("Applying preset: " + selected_preset.__name__)
        preset_preferences = get_preferences_data(selected_preset, tournament)
        for pref in preset_preferences:
            print(f"{pref['key']} : {pref['new_value']}")
            tournament.preferences[pref['key']] = pref['new_value']
