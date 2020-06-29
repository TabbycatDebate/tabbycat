from adjallocation.models import AdjudicatorInstitutionConflict, TeamInstitutionConflict
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Adds missing institution conflicts for each teams's and adjudicator's own institution."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--adjudicators-only", action="store_true",
            help="Only add for adjudicators, skip teams")
        parser.add_argument("--teams-only", action="store_true",
            help="Only add for teams, skip adjudicators")

    def handle_tournament(self, tournament, **options):
        if not options["teams_only"]:
            self.add_for_adjudicators(tournament)
        if not options["adjudicators_only"]:
            self.add_for_teams(tournament)

    def add_for_adjudicators(self, tournament):
        existing = 0
        missing = 0

        for adj in tournament.adjudicator_set.all():
            if adj.institution is None:
                continue
            _, created = AdjudicatorInstitutionConflict.objects.get_or_create(
                adjudicator=adj, institution=adj.institution,
            )
            if created:
                missing += 1
                self.stdout.write("Added self-institutional conflict for {adj.name} of "
                        "{adj.institution.name}".format(adj=adj))
            else:
                existing += 1

        self.stdout.write("Done, created {missing} previously-missing adjudicator own-institution conflicts.".format(missing=missing))
        self.stdout.write("{existing} adjudicators already had own-institution conflicts defined.".format(existing=existing))

    def add_for_teams(self, tournament):
        existing = 0
        missing = 0

        for team in tournament.team_set.all():
            if team.institution is None:
                continue
            _, created = TeamInstitutionConflict.objects.get_or_create(
                team=team, institution=team.institution,
            )
            if created:
                missing += 1
                self.stdout.write("Added self-institutional conflict for {team.short_name} of "
                        "{team.institution.name}".format(team=team))
            else:
                existing += 1

        self.stdout.write("Done, created {missing} previously-missing team own-institution conflicts.".format(missing=missing))
        self.stdout.write("{existing} teams already had own-institution conflicts defined.".format(existing=existing))
