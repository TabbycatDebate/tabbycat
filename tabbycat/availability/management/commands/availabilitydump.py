from django.db.models import Prefetch

from availability.models import RoundAvailability
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Prints a CSV-style list of adjudicator availabilities"

    def handle_tournament(self, tournament, **options):

        rounds = tournament.prelim_rounds()
        queryset = tournament.relevant_adjudicators.all()

        for rd in rounds:
            queryset = queryset.prefetch_related(Prefetch('round_availabilities',
                    queryset=RoundAvailability.objects.filter(round=rd),
                    to_attr='available_%d' % rd.seq))

        self.stdout.write("institution,name")
        for adj in queryset:
            row = [
                adj.institution.code if adj.institution else "",
                adj.name,
            ]
            row.extend([str(len(getattr(adj, 'available_%d' % rd.seq)) > 0) for rd in rounds])
            self.stdout.write(",".join(row))
