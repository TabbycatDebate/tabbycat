from utils.management.base import TournamentCommand

from ...emoji import set_emoji


class Command(TournamentCommand):

    help = "Regenerates all emoji for a given tournament's teams"

    def handle_tournament(self, tournament, **options):
        all_teams = tournament.team_set.all()
        all_teams.update(emoji=None)
        set_emoji(all_teams, tournament)
        self.stdout.write("Assigned emoji to {count} teams in tournament {tournament}".format(
                count=all_teams.count(), tournament=tournament))
