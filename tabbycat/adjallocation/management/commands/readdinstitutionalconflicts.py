from utils.management.base import TournamentCommand

from adjallocation.models import AdjudicatorInstitutionConflict


class Command(TournamentCommand):

    help = "Adds missing adjudicator-institution conflicts for each adjudicator's own institution."

    def handle_tournament(self, tournament, **options):

        existing = 0
        missing = 0

        for adj in tournament.adjudicator_set.all():
            aic, created = AdjudicatorInstitutionConflict.objects.get_or_create(
                adjudicator=adj, institution=adj.institution
            )
            if created:
                missing += 1
                self.stdout.write("Added self-institutional conflict for {adj.name} of "
                        "{adj.institution.name}".format(adj=adj))
            else:
                existing += 1

        self.stdout.write("Done, created {missing} previously-missing self-institutional conflicts.".format(missing=missing))
        self.stdout.write("{existing} adjudicators already had self-institutional conflicts defined.".format(existing=existing))
