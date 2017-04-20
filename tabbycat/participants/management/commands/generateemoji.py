from utils.management.base import TournamentCommand

from ...emoji import pick_unused_emoji


class Command(TournamentCommand):

    help = "Regenerates all emoji for a given tournament's teams"

    def handle_tournament(self, tournament, **options):
        all_teams = tournament.team_set.all()
        all_teams.update(emoji=None)
        for team in all_teams:
            team.emoji = pick_unused_emoji(all_teams)
            team.save()
        self.stdout.write("Assigned emoji to {count} teams in tournament {tournament}".format(
                count=all_teams.count(), tournament=tournament))
