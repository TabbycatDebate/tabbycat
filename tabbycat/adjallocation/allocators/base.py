import logging

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from draw.models import Debate
from participants.models import Team

from ..conflicts import ConflictsInfo, HistoryInfo

logger = logging.getLogger(__name__)

registry = {}


def register(cls):
    registry[cls.key] = cls
    return cls


class AdjudicatorAllocationError(RuntimeError):
    pass


class BaseAdjudicatorAllocator:

    def __init__(self, debates, adjudicators, round):
        self.tournament = round.tournament
        self.round = round
        self.debates = debates
        self.adjudicators = adjudicators

        if len(self.adjudicators) == 0:
            info = _("There are no available adjudicators. Ensure there are "
                     "adjudicators who have been marked as available for this "
                     "round before auto-allocating.")
            logger.info(info)
            raise AdjudicatorAllocationError(info)

        if (isinstance(debates, QuerySet) and debates.model == Debate) or \
                (isinstance(debates, list) and len(debates) > 0 and isinstance(debates[0], Debate)):
            teams = Team.objects.filter(debateteam__debate__in=debates)
        else:
            teams = None

        self.conflicts = ConflictsInfo(teams=teams, adjudicators=self.adjudicators)
        self.history = HistoryInfo(round=round)

    def allocate(self):
        raise NotImplementedError
