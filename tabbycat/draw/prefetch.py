"""Functions that prefetch data for efficiency."""

import logging

from django.db.models import OuterRef, Subquery
from django.db.models.expressions import RawSQL

from .models import Debate, DebateTeam

logger = logging.getLogger(__name__)


def populate_opponents(debateteams, speakers=True):
    """Sets the attribute `_opponent` on each DebateTeam in debateteams, to
    the DebateTeam representing their opponents.

    If `speakers` is True, it also prefetches Speaker instances.
    """

    ids = [dt.id for dt in debateteams]
    opponent_subq = DebateTeam.objects.filter(
        debate=OuterRef('debate')).exclude(id=OuterRef('id')).values('id')[:1]
    debateteams_annotated = DebateTeam.objects.filter(id__in=ids).annotate(
        opponent_id=Subquery(opponent_subq))

    debateteams_annotated_by_id = {dt.id: dt for dt in debateteams_annotated}
    opponent_ids = [dt.opponent_id for dt in debateteams_annotated]

    opponent_dts = DebateTeam.objects.select_related('team')
    if speakers:
        opponent_dts = opponent_dts.prefetch_related('team__speaker_set')
    opponent_dts = opponent_dts.in_bulk(opponent_ids)

    for dt in debateteams:
        dt_annotated = debateteams_annotated_by_id[dt.id]
        try:
            dt._opponent = opponent_dts[dt_annotated.opponent_id]
        except KeyError:
            logger.warning("No opponent found for %s", str(dt))
            dt._opponent = None


def populate_history(debates):
    """Sets the attribute _history to the number of times the teams in the
    debate have seen each other before the round of the debate."""

    debates_by_id = {debate.id: debate for debate in debates}

    debates_annotated = Debate.objects.filter(id__in=debates_by_id.keys()).annotate(
        past_debates=RawSQL("""
            SELECT DISTINCT COUNT(past_debate.id)
            FROM draw_debate AS past_debate
            JOIN draw_debateteam AS this_aff_dt ON this_aff_dt.debate_id = draw_debate.id
            JOIN draw_debateteam AS this_neg_dt ON this_neg_dt.debate_id = draw_debate.id
            JOIN tournaments_round AS this_round ON draw_debate.round_id = this_round.id
            JOIN draw_debateteam AS past_aff_dt ON past_aff_dt.debate_id = past_debate.id
            JOIN draw_debateteam AS past_neg_dt ON past_neg_dt.debate_id = past_debate.id
            JOIN tournaments_round AS past_round ON past_debate.round_id = past_round.id
            WHERE this_aff_dt.side = 'aff'
            AND   this_neg_dt.side = 'neg'
            AND   past_aff_dt.team_id = this_aff_dt.team_id
            AND   past_neg_dt.team_id = this_neg_dt.team_id
            AND   past_round.seq < this_round.seq""",
            ()),
    )

    for debate in debates_annotated:
        debates_by_id[debate.id]._history = debate.past_debates
