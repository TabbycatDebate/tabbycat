from utils.management.base import TournamentCommand
from adjallocation.models import N1RuleAssignment


class Command(TournamentCommand):

    help = "Adds missing N-1 rule institutional assignments for each adjudicator's own institution."

    def handle_tournament(self, tournament, **options):
        already_assigned = set(N1RuleAssignment.objects.filter(
            adjudicator__tournament=tournament,
            team__isnull=True,
        ).values_list('adjudicator_id', flat=True))

        new_assignments = [
            N1RuleAssignment(adjudicator=adj, institution=adj.institution)
            for adj in tournament.adjudicator_set.filter(
                institution__isnull=False,
            ).select_related('institution')
            if adj.id not in already_assigned
        ]
        N1RuleAssignment.objects.bulk_create(new_assignments)
        count = len(new_assignments)
        self.stdout.write(
            "Done, created {count} previously-missing N-1 institutional assignments.".format(count=count)
        )