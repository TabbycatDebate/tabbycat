from utils.management.base import TournamentCommand, CommandError

class Command(TournamentCommand):

    help = "Removes institution codes from team names and enables 'use institution prefix' on them. " \
           "For example, if a team's reference field is 'Auckland 1' and its institution's short" \
           "name is 'Auckland', the team's reference will be changed to '1' and its institution " \
           "prefix enabled, so it will still show as 'Auckland 1' but be represented more correctly " \
           "in the database."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--dry-run", action="store_true", help="Show what it would convert, but do not actually convert")

    def handle_tournament(self, tournament, **options):
        for team in tournament.team_set.all():
            if team.reference.startswith(team.institution.code + " "):
                new_reference = team.reference[len(team.institution.code):].strip()
                if options["dry_run"]:
                    self.stdout.write("Would rename team {!r} from {} to {!r}".format(team.reference, team.institution.code, new_reference))
                else:
                    self.stdout.write("Renaming team {!r} from {} to {!r}".format(team.reference, team.institution.code, new_reference))
                    team.reference = new_reference
                    team.use_institution_prefix = True
                    team.save()
            else:
                self.stdout.write("Leaving team {!r} from {} alone".format(team.reference, team.institution.code))
