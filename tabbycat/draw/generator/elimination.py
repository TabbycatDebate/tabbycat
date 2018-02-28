"""Draw generators for two-team elimination rounds."""

import logging

from django.utils.translation import gettext as _

from .common import BasePairDrawGenerator, DrawFatalError, DrawUserError, EliminationDrawMixin
from .pairing import Pairing
from .utils import ispow2, partial_break_round_split

logger = logging.getLogger(__name__)


class BaseEliminationDrawGenerator(EliminationDrawMixin, BasePairDrawGenerator):

    requires_even_teams = False
    DEFAULT_OPTIONS = {}

    def _make_pairings(self, teams, num_bye_rooms):
        """Folds the teams in `teams`, assigning consecutive room ranks starting
        from `num_bye_rooms+1`.  Subclasses can use this method to generate
        pairings from a list of teams."""

        debates = len(teams) // 2
        top = teams[:debates]
        bottom = teams[debates:]
        bottom.reverse()
        pairings = list()
        for i, ts in enumerate(zip(top, bottom), start=num_bye_rooms+1):
            pairing = Pairing(ts, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings


class FirstEliminationDrawGenerator(BaseEliminationDrawGenerator):
    """Class for draw for a round that is a first elimination round, with
    a number of teams breaking that is not a power of two."""

    requires_prev_results = False

    def make_pairings(self):
        if len(self.teams) < 2:
            raise DrawUserError(_("There are only %d teams breaking in this category; "
                    "there need to be at least two to generate an elimination round draw.") % len(self.teams))

        try:
            debates, bypassing = partial_break_round_split(len(self.teams))
        except AssertionError as e:
            raise DrawFatalError(e)

        logger.info("There will be %d debates in this round and %d teams bypassing it.", debates, bypassing)
        teams = self.teams[bypassing:]
        return self._make_pairings(teams, bypassing)


class SubsequentEliminationDrawGenerator(BaseEliminationDrawGenerator):
    """Class for second or subsequent elimination round.
    For this draw type, 'teams' should be the teams that automatically
    advanced to this round (i.e., bypassed the previous break round).
    'results' should be a list of Pairings with winners indicated."""

    requires_prev_results = True

    def make_pairings(self):
        self.results.sort(key=lambda x: x.room_rank)
        winners = [pairing.winner for pairing in self.results]
        if winners.count(None) > 0:
            raise DrawUserError(_("%d debates in the previous round don't have a result.") % winners.count(None))

        bypassing = self.results[0].room_rank - 1  # e.g. if lowest room rank was 7, then 6 teams should bypass
        teams = self.teams[:bypassing] + winners
        logger.info("%d teams bypassed the previous round and %d teams won the last round" % (bypassing, len(winners)))

        if not ispow2(len(teams)):
            raise DrawUserError(_("The number of teams (%d) in this round is not a power of two.") % len(teams))

        return self._make_pairings(teams, 0)
