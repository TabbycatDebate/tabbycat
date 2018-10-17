import logging

from django.utils.translation import gettext as _

from participants.models import Team
from utils.views import BadJsonRequestError

from .conflicts import ConflictsInfo, HistoryInfo

logger = logging.getLogger(__name__)


def legacy_allocate_adjudicators(round, alloc_class):
    """@depracate when legacy drag and drop UIs removed"""
    if round.draw_status != round.STATUS_CONFIRMED:
        raise RuntimeError("Tried to allocate adjudicators on unconfirmed draw")

    debates = round.debate_set.all()
    adjs = list(round.active_adjudicators.all())
    allocator = alloc_class(debates, adjs, round)

    for alloc in allocator.allocate():
        alloc.save()

    round.adjudicator_status = round.STATUS_DRAFT
    round.save()


class Allocator(object):
    def __init__(self, debates, adjudicators, round):
        self.tournament = round.tournament
        self.round = round
        self.debates = list(debates)
        self.adjudicators = adjudicators

        if len(self.adjudicators) == 0:
            info = _("There are no available adjudicators. Ensure there are "
                     "adjudicators who have been marked as available for this "
                     "round before auto-allocating.")
            logger.info(info)
            raise BadJsonRequestError(info)

        teams = Team.objects.filter(debateteam__debate__in=debates)
        self.conflicts = ConflictsInfo(teams=teams, adjudicators=self.adjudicators)
        self.history = HistoryInfo(round=round)

    def allocate(self):
        raise NotImplementedError
