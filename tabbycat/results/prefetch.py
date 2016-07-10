"""Functions that prefetch data for efficiency."""

from .models import TeamScore


def populate_wins(debates):
    """Sets an attribute `_win` on each DebateTeam in each Debate, representing
    whether they won the debate. For best results, the caller should already
    have run populate_teams(debates) in draw/prefetch.py before calling this
    function.

    This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.
    """

    debateteams = [dt for debate in debates for dt in [debate.aff_dt, debate.neg_dt]]
    debateteams_by_id = {dt.id: dt for dt in debateteams}

    teamscores = TeamScore.objects.filter(debate_team__debate__in=debates, ballot_submission__confirmed=True)

    for teamscore in teamscores:
        debateteam = debateteams_by_id[teamscore.debate_team_id]
        debateteam._win = teamscore.win

    # populate the attribute for DebateTeams that don't have a result
    for debateteam in debateteams:
        if not hasattr(debateteam, "_win"):
            debateteam._win = None
