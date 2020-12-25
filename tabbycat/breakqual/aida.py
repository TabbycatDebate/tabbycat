"""Break generators relating to the Australasian Intervarsity Debating
Association (AIDA)."""

import logging
import math

from itertools import groupby

from breakqual.models import BreakingTeam

from .base import register, StandardBreakGenerator

logger = logging.getLogger(__name__)


class BaseAidaBreakGenerator(StandardBreakGenerator):
    key = None
    rankings = ('rank', 'institution_rank')
    institution_cap = 3

    def compute_break(self):
        self.exclude_capped_teams()
        super().compute_break()

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""
        raise NotImplementedError


@register
class Aida1996BreakGenerator(BaseAidaBreakGenerator):
    key = "aida-1996"

    def compute_break(self):
        self.exclude_capped_teams()
        super().compute_break()

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""

        self.capped_teams = []

        for tsi in self.eligible_teams:
            institution_rank = tsi.get_ranking("institution")
            if institution_rank > self.institution_cap:
                logger.info("Capped out, institution rank %d, cap %d: %s", institution_rank, self.institution_cap, tsi.team)
                self.capped_teams.append(tsi)

        for tsi in self.capped_teams:
            self.eligible_teams.remove(tsi)
            self.excluded_teams[tsi] = BreakingTeam.REMARK_CAPPED


class BaseAida2016BreakGenerator(BaseAidaBreakGenerator):
    required_metrics = ('wins',)

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""

        if len(self.eligible_teams) < self.break_size:
            return

        # ii. Discard teams with fewer wins than the nth ranked team
        min_wins = self.eligible_teams[self.break_size-1].metrics["wins"]
        self.eligible_teams = [tsi for tsi in self.eligible_teams if tsi.metrics["wins"] >= min_wins]

        # natural_break_cutoff is the (true) rank of the last breaking team,
        # not allowing for the cap but allowing for ineligible teams.
        natural_break_cutoff = self.eligible_teams[self.break_size-1].get_ranking("rank")
        self.capped_teams = []

        # iii. Set aside teams that are capped out
        for tsi in self.eligible_teams:
            institution_rank = tsi.get_ranking("institution")
            if institution_rank is None:
                continue
            elif institution_rank > 1 and tsi.get_ranking("rank") > natural_break_cutoff:
                logger.info("Capped out post-cutoff, institution rank %d: %s", institution_rank, tsi.team)
                self.capped_teams.append(tsi)
            elif institution_rank > self.institution_cap:
                logger.info("Capped out pre-cutoff, institution rank %d, cap %d: %s", institution_rank, self.institution_cap, tsi.team)
                self.capped_teams.append(tsi)

        # iv. Reinsert capped teams if there are too few breaking
        # Easters and Australs have different procedures for reinsertion.
        self.reinsert_capped_teams()

        # Now, exclude capped teams accordingly
        for tsi in self.capped_teams:
            self.eligible_teams.remove(tsi)
            self.excluded_teams[tsi] = BreakingTeam.REMARK_CAPPED

    def reinsert_capped_teams(self):
        """Unexcludes teams that were subject to the post-cutoff cap if there
        are too few teams breaking."""
        raise NotImplementedError

    def _reinsert_capped_teams(self, teams_eligible_for_reinsertion):
        """Used by subclasses to implement self.reinsert_capped_teams()"""

        if len(self.eligible_teams) - len(self.capped_teams) >= self.break_size:
            return

        reinsert = []
        number_to_reinsert = self.break_size - len(self.eligible_teams) + len(self.capped_teams)

        for _, group in groupby(teams_eligible_for_reinsertion, key=lambda tsi: tuple(tsi.itermetrics())):
            group = list(group)
            reinsert.extend(group)
            logger.info("Reinserting: %s", str(group))
            if len(reinsert) >= number_to_reinsert:
                tsi = group[-1]
                excess = len(reinsert) - number_to_reinsert
                logger.info("Break rank correction: %d at %s", excess, tsi.team)
                self.break_rank_correction = tsi, excess
                break

        for tsi in reinsert:
            self.capped_teams.remove(tsi)


class BaseAida2016AustralsBreakGenerator(BaseAida2016BreakGenerator):
    def reinsert_capped_teams(self):
        self._reinsert_capped_teams(self.capped_teams)


@register
class Aida2016EastersBreakGenerator(BaseAida2016BreakGenerator):
    key = "aida-2016-easters"

    def reinsert_capped_teams(self):
        # Easters rules give teams capped out post-cutoff priority
        post_cutoff_capped_teams = [tsi for tsi in self.capped_teams
            if tsi.get_ranking("institution") <= self.institution_cap]
        self._reinsert_capped_teams(post_cutoff_capped_teams)
        self._reinsert_capped_teams(self.capped_teams)


@register
class Aida2016AustralsBreakGenerator(BaseAida2016AustralsBreakGenerator):
    key = "aida-2016-australs"


@register
class Aida2019AustralsBreakGenerator(BaseAida2016AustralsBreakGenerator):
    """Calculates the number of teams by which the break exceeds the base of 16
    teams. Then expands the institutional cap by 1 team for every 8 additional
    teams."""
    key = "aida-2019-australs-open"

    def compute_break(self):
        self.calculate_cap()
        super().compute_break()

    def calculate_cap(self):
        additional_teams = self.break_size - 16 if self.break_size >= 16 else 0
        self.institution_cap = 3 + math.floor(additional_teams / 8)
        logger.info("Break size of %d teams exceeds the 16-team base by %d. The institutional cap is set at %d.",
                self.break_size, additional_teams, self.institution_cap)
