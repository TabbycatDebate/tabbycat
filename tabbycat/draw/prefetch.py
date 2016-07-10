"""Functions that prefetch data for efficiency."""

from .models import DebateTeam


def populate_teams(debates, speakers=True):
    """Sets attributes `_aff_dt`, `_aff_team`, `_neg_dt`, `_neg_team` on each
    debate in `debates`, each being the appropriate Team or DebateTeam.
    This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.

    If `speakers` is True, it also prefetches Speaker instances.
    """
    debates_by_id = {debate.id: debate for debate in debates}

    debateteams = DebateTeam.objects.filter(debate__in=debates).select_related('team')
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
