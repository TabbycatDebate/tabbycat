"""Functions that prefetch data for efficiency."""

import logging

from django.db.models.expressions import RawSQL

from .models import Debate, DebateTeam

logger = logging.getLogger(__name__)


def populate_teams(debates, speakers=True, institutions=False):
    """Sets attributes `_aff_dt`, `_aff_team`, `_neg_dt`, `_neg_team` on each
    debate in `debates`, each being the appropriate Team or DebateTeam.
    This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.

    If `speakers` is True, it also prefetches Speaker instances.
    """
    debates_by_id = {debate.id: debate for debate in debates}

    debateteams = DebateTeam.objects.filter(debate__in=debates).select_related('team', 'team__institution')
    if speakers:
        debateteams = debateteams.prefetch_related('team__speaker_set')
    for debateteam in debateteams:
        debate = debates_by_id[debateteam.debate_id]
        if debateteam.position == DebateTeam.POSITION_AFFIRMATIVE:
            debate._aff_dt = debateteam
            debate._aff_team = debateteam.team
        elif debateteam.position == DebateTeam.POSITION_NEGATIVE:
            debate._neg_dt = debateteam
            debate._neg_team = debateteam.team


def populate_opponents(debateteams, speakers=True):
    """Sets the attribute `_opponent` on each DebateTeam in debateteams, to
    the DebateTeam representing their opponents.

    If `speakers` is True, it also prefetches Speaker instances.
    """

    ids = [dt.id for dt in debateteams]
    debateteams_annotated = DebateTeam.objects.filter(id__in=ids).annotate(
        opponent_id=RawSQL("""
        SELECT opponent.id
        FROM draw_debateteam AS opponent
        WHERE opponent.debate_id = draw_debateteam.debate_id
        AND opponent.id != draw_debateteam.id""", ())
    )
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
            WHERE this_aff_dt.position = 'A'
            AND   this_neg_dt.position = 'N'
            AND   past_aff_dt.team_id = this_aff_dt.team_id
            AND   past_neg_dt.team_id = this_neg_dt.team_id
            AND   past_round.seq < this_round.seq""",
            ()),
    )

    for debate in debates_annotated:
        debates_by_id[debate.id]._history = debate.past_debates
