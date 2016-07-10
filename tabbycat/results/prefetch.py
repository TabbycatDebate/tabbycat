"""Functions that prefetch data for efficiency."""

from .models import BallotSubmission, TeamScore


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


def populate_confirmed_ballots(debates, motions=False):
    """Sets an attribute `_confirmed_ballot` on each Debate, each being the
    BallotSubmission instance for that debate.

    This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.
    """
    debates_by_id = {debate.id: debate for debate in debates}
    confirmed_ballots = BallotSubmission.objects.filter(debate__in=debates, confirmed=True)
    if motions:
        confirmed_ballots = confirmed_ballots.select_related('motion')

    for ballotsub in confirmed_ballots:
        debate = debates_by_id[ballotsub.debate_id]
        debate._confirmed_ballot = ballotsub

    # populate the attribute for Debates that don't have a confirmed ballot
    for debate in debates:
        if not hasattr(debate, "_confirmed_ballot"):
            debate._confirmed_ballot = None
