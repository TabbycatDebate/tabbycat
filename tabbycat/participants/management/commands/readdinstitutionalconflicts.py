from utils.management.base import TournamentCommand

from adjallocation.models import AdjudicatorInstitutionConflict


class Command(TournamentCommand):

    help = "Goes through and adds missing Adjudicator-Institution conflicts for each adjudicator's own institution."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle_tournament(self, tournament, **options):

        for adj in tournament.adjudicator_set.all():
            conflict_check = AdjudicatorInstitutionConflict.objects.filter(adjudicator=adj,
                institution=adj.institution).exists()
            if not conflict_check:
                self_conflict = AdjudicatorInstitutionConflict(adjudicator=adj,
                institution=adj.institution)
                self_conflict.save()
                self.stdout.write("Adding self-institutional conflict for {}".format(adj.name))

