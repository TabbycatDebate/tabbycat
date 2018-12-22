from adjallocation.models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                                  AdjudicatorTeamConflict, TeamInstitutionConflict)
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Prints CSV-style exports of conflicts"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--full-institution-name", action="store_true", default=False,
            help="Use full institution name (rather than code)")
        parser.add_argument("--include-own-institution", action="store_true", default=False,
            help="Include own-institution conflicts")

    def handle_tournament(self, tournament, **options):

        self.stdout.write(" === Adjudicator-team conflicts ===")
        self.stdout.write("adjudicator,team")
        for conflict in AdjudicatorTeamConflict.objects.filter(
                adjudicator__tournament=tournament, team__tournament=tournament):
            self.stdout.write(",".join([conflict.adjudicator.name, conflict.team.short_name]))
        self.stdout.write("")

        self.stdout.write(" === Adjudicator-adjudicator conflicts ===")
        self.stdout.write("adjudicator1,adjudicator2")
        for conflict in AdjudicatorAdjudicatorConflict.objects.filter(
                adjudicator1__tournament=tournament, adjudicator2__tournament=tournament):
            self.stdout.write(",".join([conflict.adjudicator1.name, conflict.adjudicator2.name]))
        self.stdout.write("")

        self.stdout.write(" === Adjudicator-institution conflicts ===")
        self.stdout.write("adjudicator,institution")
        for conflict in AdjudicatorInstitutionConflict.objects.filter(adjudicator__tournament=tournament):
            if options['include_own_institution'] or conflict.adjudicator.institution != conflict.institution:
                self.stdout.write(",".join([conflict.adjudicator.name,
                    conflict.institution.name if options['full_institution_name']
                    else conflict.institution.code]))
        self.stdout.write("")

        self.stdout.write(" === Team-institution conflicts ===")
        self.stdout.write("team,institution")
        for conflict in TeamInstitutionConflict.objects.filter(team__tournament=tournament):
            if options['include_own_institution'] or conflict.team.institution != conflict.institution:
                self.stdout.write(",".join([conflict.team.short_name,
                    conflict.institution.name if options['full_institution_name']
                    else conflict.institution.code]))
