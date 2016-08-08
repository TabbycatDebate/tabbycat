"""Break generators relating to the Western Australia Debating League (WADL)."""

import logging

from .base import BaseBreakGenerator, register

logger = logging.getLogger(__name__)


@register
class WadlDivisionWinnersFirstBreakGenerator(BaseBreakGenerator):
    key = "wadl-div-first"
    rankings = ('rank', 'division')

    def compute_break(self):

        # First, grab division winners
        self.breaking_teams = [tsi for tsi in self.eligible_teams
                if tsi.get_ranking("division") == 1]

        num_vacant_slots = self.break_size - len(self.breaking_teams)

        if num_vacant_slots < 0:
            return

        # Then, if there are still spots to fill, add the top division non-winners
        division_losers = [tsi for tsi in self.eligible_teams
                if tsi.get_ranking("division") != 1]
        top_division_losers = division_losers[:num_vacant_slots]

        if top_division_losers:
            last_rank = top_division_losers[-1].get_ranking("rank")
            for tsi in division_losers[num_vacant_slots:]:
                if tsi.get_ranking("rank") != last_rank:
                    break
                top_division_losers.append(tsi)

        self.breaking_teams.extend(top_division_losers)


@register
class WadlDivisionWinnersGuaranteedBreakGenerator(WadlDivisionWinnersFirstBreakGenerator):
    key = "wadl-div-guaranteed"

    def compute_break(self):
        # As for division-winners-first, but sort by rank so that ranks are
        # clean.
        super().compute_break()
        self.breaking_teams.sort(key=lambda tsi: tsi.get_ranking("rank"))
