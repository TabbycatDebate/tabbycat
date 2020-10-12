from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Removes institution codes from team names and enables 'use institution prefix' on them. " \
           "For example, if a team's reference field is 'Auckland 1' and its institution's short" \
           "name is 'Auckland', the team's reference will be changed to '1' and its institution " \
           "prefix enabled, so it will still show as 'Auckland 1' but be represented more correctly " \
           "in the database."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--dry-run", action="store_true",
                            help="Show what it would convert, but do not actually convert")

    def handle_tournament(self, tournament, **options):
        for team in tournament.team_set.all():
            if team.reference.startswith(team.institution.code + " "):
                new_reference = team.reference[len(team.institution.code):].strip()
                self.stdout.write("{verb} team {!r} from {} to {!r}".format(
                    team.reference, team.institution.code, new_reference,
                    verb="Would rename" if options["dry_run"] else "Renaming"))

                if options["dry_run"]:
                    team.reference = new_reference
                    team.use_institution_prefix = True
                    team.save()
            else:
                self.stdout.write("{verb} team {!r} from {} alone".format(
                    team.reference, team.institution.code,
                    verb="Would leave" if options["dry_run"] else "Leaving"))
