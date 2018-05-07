from django.utils.translation import gettext as _

from .common import BaseBPDrawGenerator, DrawFatalError, DrawUserError, EliminationDrawMixin
from .pairing import BPPairing
from .utils import ispow2


class BaseBPEliminationDrawGenerator(EliminationDrawMixin, BaseBPDrawGenerator):

    requires_even_teams = False
    DEFAULT_OPTIONS = {}

    def _four_way_fold(self, teams, start_rank=0):
        """Returns pairings folded four-way, with room ranks numbered from
        start_rank+1."""
        if len(teams) % 4 != 0:
            raise DrawFatalError("Tried to do a four-way fold with non-multiple of four: %d" % len(teams))

        n = len(teams) // 4  # number of debates
        pools = (teams[0:n], teams[n:2*n], teams[2*n:3*n], teams[3*n:4*n])
        pools[1].reverse()
        pools[3].reverse()
        pairings = list()
        for i, ts in enumerate(zip(*pools), start=start_rank+1):
            pairing = BPPairing(ts, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings

    def _get_advancing_teams(self):
        """Collates the advancing teams from `self.results`, checks them for
        validity, and returns them in a list of lists, ordered by room rank."""
        self.results.sort(key=lambda x: x.room_rank)
        advancing = [pairing.advancing for pairing in self.results]
        advancing_counts = [len(teams) for teams in advancing]
        if advancing_counts.count(0) > 0:
            raise DrawUserError(_("%d debates in the previous round don't have a result.") % advancing_counts.count(0))
        if advancing_counts.count(2) != len(advancing_counts):
            raise DrawUserError(_("%d debates in the previous round don't have exactly two "
                "teams advancing.") % (len(advancing_counts) - advancing_counts.count(2)))
        return advancing


class PartialBPEliminationDrawGenerator(BaseBPEliminationDrawGenerator):
    """For a partial elimination round, i.e., the first elimination round where
    the break is 6*2^n."""

    def make_pairings(self):
        nteams = len(self.teams)
        if nteams % 6 != 0 or not ispow2(nteams // 6):
            # This should have been caught by the draw manager
            raise DrawFatalError("Tried to do a partial elimination draw with invalid break size: %d" % nteams)

        # Take the non-bypassing teams and fold four-way
        # Convention is to label room ranks after the highest ranked team in the
        # room, e.g. in partial octos, the room ranks go from 9 to 12
        start = nteams // 3
        teams = self.teams[start:]
        return self._four_way_fold(teams, start)


class AfterPartialBPEliminationDrawGenerator(BaseBPEliminationDrawGenerator):
    """For the round immediately following a partial elimination round, i.e.,
    the second elimination round where the break size is 6*2^n."""

    requires_prev_results = True

    def make_pairings(self):
        # e.g. if lowest room rank was 9, then 8 teams should bypass
        nbypassing = min([pairing.room_rank for pairing in self.results]) - 1
        if nbypassing % 2 != 0:
            raise DrawUserError(_("The room ranks of the partial elimination round indicate that "
                "an odd number of teams (%(nbypassing)d) bypassed it.") % {'nbypassing': nbypassing})
        ndebates = nbypassing // 2
        if len(self.results) != ndebates:
            raise DrawUserError(_("The room ranks of the partial elimination round indicate "
                "that %(nbypassing)d teams bypassed it, but %(advancing)d teams advanced from "
                "it." % {'nbypassing': nbypassing, 'nadvancing': ndebates * 2}))

        # Fold the bypassing teams two-way
        bypassing = self.teams[:nbypassing]
        bypassing_top = bypassing[:ndebates]
        bypassing_bottom = bypassing[ndebates:]
        bypassing_bottom.reverse()

        # Get (and check) the advancing teams
        advancing = self._get_advancing_teams()

        # Pair them together
        if len(advancing) != ndebates:
            # This should have been caught in one of the errors above
            raise DrawFatalError("%d advancing pairs, but %d debates from bypassing pairs" % (len(advancing), ndebates))

        pairings = list()
        for i, (team1, team2, adv) in enumerate(zip(bypassing_top, bypassing_bottom, advancing), start=1):
            teams = [team1, team2] + adv
            pairing = BPPairing(teams, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings


class FirstBPEliminationDrawGenerator(BaseBPEliminationDrawGenerator):
    """For the first elimination round where the break size is 4*2^n."""

    def make_pairings(self):
        nteams = len(self.teams)
        if nteams % 4 != 0 or not ispow2(nteams // 4):
            # This should have been caught by the draw manager
            raise DrawFatalError("Tried to do a first elimination draw with invalid break size: %d" % nteams)

        return self._four_way_fold(self.teams)


class SubsequentBPEliminationDrawGenerator(BaseBPEliminationDrawGenerator):
    """For all elimination rounds after the first one if the break size is
    4*2^n, or after the second one if the break size is 6*2^n."""

    requires_prev_results = True

    def make_pairings(self):
        advancing = self._get_advancing_teams()
        if not (len(advancing) >= 2 and ispow2(len(advancing))):
            raise DrawUserError(_("The number of debates (%d) in the last round is not a "
                "power of two.") % (2 * len(advancing)))

        # Fold the pairs of advancing teams
        ndebates = len(advancing) // 2
        top = advancing[:ndebates]
        bottom = advancing[ndebates:]
        bottom.reverse()
        pairings = list()
        for i, (teams1, teams2) in enumerate(zip(top, bottom), start=1):
            teams = teams1 + teams2  # join lists
            pairing = BPPairing(teams, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings
