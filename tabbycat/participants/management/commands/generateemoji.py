from utils.management.base import TournamentCommand

from ...emoji import get_emoji, initialise_emoji_options


class Command(TournamentCommand):

    help = "Regenerates all emoji for a given tournament's teams"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle_tournament(self, tournament, **options):
        all_teams = tournament.team_set.all()

        for team in all_teams:
            team.emoji = None
            team.save()

        for team in all_teams:
            emoji_options = initialise_emoji_options(all_teams)
            team.emoji = get_emoji(emoji_options)
            team.save()
