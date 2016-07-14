from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Resaves all teams which updates their short and long name fields. " \
           "This shouldn't generally be necessary, because the names are " \
           "auto-populated whenever institutions and teams are saved, but it " \
           "can be used when there was a mishap with team names."

    def handle_tournament(self, tournament, **options):
        for team in tournament.team_set.all():
            old_names = team.long_name + " (" + team.short_name + ")"
            team.save()
            new_names = team.long_name + " (" + team.short_name + ")"
            self.stdout.write("Resaved %s as %s" % (old_names, new_names))
