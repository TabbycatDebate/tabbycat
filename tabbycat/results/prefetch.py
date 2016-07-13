"""Functions that prefetch data for efficiency."""

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam
from motions.models import DebateTeamMotionPreference

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore
from .result import BallotSet, Scoresheet


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


def populate_confirmed_ballots(debates, motions=False, ballotsets=False):
    """Sets an attribute `_confirmed_ballot` on each Debate, each being the
    BallotSubmission instance for that debate.

    All of the debates are assumed to be from the same tournament as the first.

    This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.

    It may by advisable to call populate_allocations(debates) (in
    adjallocation.allocation) on `debates` before calling this function.
    """
    debates_by_id = {debate.id: debate for debate in debates}
    confirmed_ballots = BallotSubmission.objects.filter(debate__in=debates, confirmed=True)
    if motions:
        confirmed_ballots = confirmed_ballots.select_related('motion')
    if ballotsets:
        confirmed_ballots = confirmed_ballots.select_related('debate') # BallotSet fetches the debate

    for ballotsub in confirmed_ballots:
        debate = debates_by_id[ballotsub.debate_id]
        debate._confirmed_ballot = ballotsub

    # populate the attribute for Debates that don't have a confirmed ballot
    for debate in debates:
        if not hasattr(debate, "_confirmed_ballot"):
            debate._confirmed_ballot = None

    try:
        POSITIONS = debates[0].round.tournament.POSITIONS  # noqa
    except IndexError:
        return

    if ballotsets:

        debateteams_by_debate_id = {}
        ballotsets_by_debate_id = {}
        ballotsets_by_ballotsub_id = {}

        # Populate debateteams
        debateteams = DebateTeam.objects.filter(debate__in=debates).select_related('team')
        for dt in debateteams:
            debateteams_by_debate_id.setdefault(dt.debate_id, []).append(dt)

        # Create the BallotSets
        # ---------------------
        for ballotsub in confirmed_ballots:
            ballotset = BallotSet(ballotsub, load=False)
            ballotset.debate = debates_by_id[ballotsub.debate_id] # this instance is probably prefetched
            ballotset.POSITIONS = POSITIONS
            ballotset.update_debateteams(debateteams_by_debate_id[ballotsub.debate_id])
            ballotset.init_blank_buffer()
            ballotset._adjudicator_sheets = {}
            ballotset._sheets_created = True

            ballotsub._ballot_set = ballotset
            ballotsets_by_debate_id[ballotsub.debate_id] = ballotset
            ballotsets_by_ballotsub_id[ballotsub.id] = ballotset

        # Populate speaker positions
        speakerscores = SpeakerScore.objects.filter(
                ballot_submission__in=confirmed_ballots).select_related('debate_team')
        for ss in speakerscores:
            ballotset = ballotsets_by_ballotsub_id[ss.ballot_submission_id]
            ballotset.speakers[ss.debate_team][ss.position] = ss.speaker

        # Populate teamscores
        teamscores = TeamScore.objects.filter(
                ballot_submission__in=confirmed_ballots).select_related('debate_team')
        for ts in teamscores:
            ballotset = ballotsets_by_ballotsub_id[ts.ballot_submission_id]
            ballotset.teamscore_objects[ts.debate_team] = ts.debate_team

        # Populate motion vetoes
        dtmps = DebateTeamMotionPreference.objects.filter(
                ballot_submission__in=confirmed_ballots, preference=3).select_related(
                'debate_team', 'motion')
        for dtmp in dtmps:
            ballotset = ballotsets_by_ballotsub_id[dtmp.ballot_submission_id]
            ballotset.motion_veto[dtmp.debate_team] = dtmp.motion

        # Create the Scoresheets
        # ----------------------
        scoresheets_by_debateadj_id = {}
        debateadjs = DebateAdjudicator.objects.filter(
                debate__in=ballotsets_by_debate_id.keys()).exclude(
                type=DebateAdjudicator.TYPE_TRAINEE).select_related('adjudicator')
        for da in debateadjs:
            ballotset = ballotsets_by_debate_id[da.debate_id]
            scoresheet = Scoresheet(ballotset.ballotsub, da.adjudicator, load=False)
            scoresheet.da = da
            scoresheet.POSITIONS = POSITIONS
            scoresheet.update_debateteams(debateteams_by_debate_id[da.debate_id])
            scoresheet.init_blank_buffer()

            ballotset._adjudicator_sheets[da.adjudicator] = scoresheet
            scoresheets_by_debateadj_id[da.id] = scoresheet

        ssbas = SpeakerScoreByAdj.objects.filter(debate_team__debate__in=debates,
                ballot_submission__in=confirmed_ballots,
                debate_adjudicator__in=debateadjs).select_related('debate_team')
        for ssba in ssbas:
            scoresheet = scoresheets_by_debateadj_id[ssba.debate_adjudicator_id]
            scoresheet._set_score(ssba.debate_team, ssba.position, ssba.score)

        # Finally, check that everything is in order
        # ------------------------------------------
        for ballotsub in confirmed_ballots:
            ballotsub.ballot_set.assert_loaded()
