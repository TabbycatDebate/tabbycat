"""Functions that prefetch data for efficiency."""

import logging

from django.db.models import Count, OuterRef, Subquery
from django.db.models.expressions import RawSQL

from .models import Debate, DebateTeam
from .types import DebateSide

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
            WHERE this_aff_dt.side = %d
            AND   this_neg_dt.side = %d
            AND   past_aff_dt.team_id = this_aff_dt.team_id
            AND   past_neg_dt.team_id = this_neg_dt.team_id
            AND   past_round.seq < this_round.seq""" % (DebateSide.AFF.value, DebateSide.NEG.value),
            ()),
    )

    for debate in debates_annotated:
        debates_by_id[debate.id]._history = debate.past_debates


def populate_pullup_counts(debates):
    """Sets _pullup_count on each DebateTeam, giving the total number of times
    that team has been pulled up up to and including the current round."""
    if not debates:
        return

    round_seq = debates[0].round.seq
    tournament = debates[0].round.tournament

    debateteams = [dt for debate in debates for dt in debate.debateteams]
    if not debateteams:
        return

    team_ids = [dt.team_id for dt in debateteams]

    counts = DebateTeam.objects.filter(
        team_id__in=team_ids,
        debate__round__tournament=tournament,
        debate__round__seq__lte=round_seq,
        flags__contains=['pullup'],
    ).values('team_id').annotate(count=Count('id'))

    counts_by_team = {row['team_id']: row['count'] for row in counts}

    for dt in debateteams:
        dt._pullup_count = counts_by_team.get(dt.team_id, 0)
