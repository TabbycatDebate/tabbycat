from utils.management.base import TournamentCommand

from adjallocation.models import AdjudicatorInstitutionConflict


class Command(TournamentCommand):

    help = "Adds missing adjudicator-institution conflicts for each adjudicator's own institution."

    def handle_tournament(self, tournament, **options):

        for adj in tournament.adjudicator_set.all():
            aic, created = AdjudicatorInstitutionConflict.objects.get_or_create(
                adjudicator=adj, institution=adj.institution
            )
            if created:
                self.stdout.write("Added self-institutional conflict for {adj.name} of "
                        "{adj.institution.name}".format(adj=adj))
