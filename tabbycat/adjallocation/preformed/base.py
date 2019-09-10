import logging

from django.db.models import Prefetch
from django.utils.translation import gettext as _

from adjallocation.models import PreformedPanelAdjudicator
from participants.models import Adjudicator, Team

from ..allocators.base import AdjudicatorAllocationError
from ..conflicts import ConflictsInfo, HistoryInfo

logger = logging.getLogger(__name__)

registry = {}


def register(cls):
    registry[cls.key] = cls
    return cls


class BasePreformedPanelAllocator:
    """Base class for preformed panel allocators.

    A preformed panel allocators allocates preformed panels (which must already
    exist in the database) to debates. It should be run after preformed panels
    have been created *and* the draw for the relevant round has been created.
    """

    def __init__(self, debates, panels, round):
        """`debates` and `panels` must both be QuerySets, not other iterables."""

        self.tournament = round.tournament
        self.round = round
        self.debates = debates
        self.panels = panels.prefetch_related(
            Prefetch('preformedpaneladjudicator_set',
                queryset=PreformedPanelAdjudicator.objects.select_related('adjudicator')))

        if len(self.panels) == 0:
            info = _("There are no preformed panels to use. Have you allocated "
                     "preformed panels for this round? If not, try just auto-allocating "
                     "adjudicators instead.")
            logger.info(info)
            raise AdjudicatorAllocationError(info)

        teams = Team.objects.filter(debateteam__debate__in=debates)
        adjudicators = Adjudicator.objects.filter(preformedpaneladjudicator__panel__in=panels)
        self.conflicts = ConflictsInfo(teams=teams, adjudicators=adjudicators)
        self.history = HistoryInfo(round=round)

    def allocate(self):
        """Must return a tuple of two lists: a list of `Debate` instances, and
        a list of `PreformedPanel` instances, presumably those in `self.debates`
        and `self.panels`. The list of panels (but not the list of debates) may
        have `None` in it, to indicate that the corresponding debate should have
        its adjudicators cleared."""
        raise NotImplementedError
