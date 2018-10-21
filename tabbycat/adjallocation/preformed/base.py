import logging

from django.db.models import Prefetch
from django.utils.translation import gettext as _

from adjallocation.models import PreformedPanelAdjudicator
from participants.models import Adjudicator, Team
from utils.views import BadJsonRequestError

from ..conflicts import ConflictsInfo, HistoryInfo

logger = logging.getLogger(__name__)


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
            raise BadJsonRequestError(info)

        teams = Team.objects.filter(debateteam__debate__in=debates)
        adjudicators = Adjudicator.objects.filter(preformedpaneladjudicator__panel__in=panels)
        self.conflicts = ConflictsInfo(teams=teams, adjudicators=adjudicators)
        self.history = HistoryInfo(round=round)

    def allocate(self):
        allocations = self.get_allocations()
        self.write_allocations_to_db(allocations)

    def write_allocations_to_db(self, allocations):
        """Writes the given allocations to the database, wiping existing
        adjudicator allocations for the given debates if there are any.
        `allocations` must be an iterable of 2-tuples `(panel, debate)`,
        where `panel` is a `PreformedPanel` and `debate` is a `Debate`."""
        for debate, panel in allocations:
            debate.debateadjudicator_set.all().delete()
            for ppa in panel.preformedpaneladjudicator_set.all():
                debate.debateadjudicator_set.create(adjudicator=ppa.adjudicator, type=ppa.type)

    def get_allocations(self):
        raise NotImplementedError
