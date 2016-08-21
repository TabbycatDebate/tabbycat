"""Functions that prefetch data for efficiency."""

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam
from motions.models import DebateTeamMotionPreference
from tournaments.models import Tournament

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

    For best performance, the debates should already have
    debateadjudicator_set__adjudicator prefetched.
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

    if ballotsets:
        populate_ballotsets(confirmed_ballots, debates)


def populate_ballotsets(ballotsubs, prefetched_debates=[]):
    """Populates the `_ballot_set` attribute of each BallotSubmission in
    `ballotsubs` with a populated BallotSet instance.

    If `prefetched_debates` is provided, debates in that list will be used
    as `ballotset.debate` where appropriate, rather than `ballotsub.debate`.

    If `prefetched_debates` is not provided, then for best performance,
    the ballot submissions should already have their debates prefetched
    (using select_related).
    """

    if not ballotsubs:
        return

    POSITIONS = Tournament.objects.get(round__debate__ballotsubmission=ballotsubs[0]).POSITIONS  # noqa: N806

    prefetched_debates_by_id = {debate.id: debate for debate in prefetched_debates}
    debateteams_by_debate_id = {}
    ballotsets_by_debate_id = {}
    ballotsets_by_ballotsub_id = {}

    # Populate debateteams
    debateteams = DebateTeam.objects.filter(debate__ballotsubmission__in=ballotsubs).select_related('team').distinct()
    for dt in debateteams:
        debateteams_by_debate_id.setdefault(dt.debate_id, []).append(dt)

    # Create the BallotSets
    # ---------------------
    for ballotsub in ballotsubs:
        ballotset = BallotSet(ballotsub, load=False)
        ballotset.debate = prefetched_debates_by_id.get(ballotsub.debate_id, ballotsub.debate)
        ballotset.POSITIONS = POSITIONS
        ballotset.update_debateteams(debateteams_by_debate_id[ballotsub.debate_id])
        ballotset.init_blank_buffer()
        ballotset._adjudicator_sheets = {}
        ballotset._sheets_created = True

        ballotsub._ballot_set = ballotset
        ballotsets_by_debate_id.setdefault(ballotsub.debate_id, []).append(ballotset)
        ballotsets_by_ballotsub_id[ballotsub.id] = ballotset

    # Populate speaker positions
    speakerscores = SpeakerScore.objects.filter(
            ballot_submission__in=ballotsubs).select_related('debate_team')
    for ss in speakerscores:
        ballotset = ballotsets_by_ballotsub_id[ss.ballot_submission_id]
        ballotset.speakers[ss.debate_team][ss.position] = ss.speaker

    # Populate teamscores
    teamscores = TeamScore.objects.filter(
            ballot_submission__in=ballotsubs).select_related('debate_team')
    for ts in teamscores:
        ballotset = ballotsets_by_ballotsub_id[ts.ballot_submission_id]
        ballotset.teamscore_objects[ts.debate_team] = ts.debate_team

    # Populate motion vetoes
    dtmps = DebateTeamMotionPreference.objects.filter(
            ballot_submission__in=ballotsubs, preference=3).select_related(
            'debate_team', 'motion')
    for dtmp in dtmps:
        ballotset = ballotsets_by_ballotsub_id[dtmp.ballot_submission_id]
        ballotset.motion_veto[dtmp.debate_team] = dtmp.motion

    # Create the Scoresheets
    # ----------------------
    scoresheets_by_ballotsub_and_debateadj_id = {}
    debateadjs = DebateAdjudicator.objects.filter(debate__ballotsubmission__in=ballotsubs).exclude(
            type=DebateAdjudicator.TYPE_TRAINEE).select_related('adjudicator').distinct()
    for da in debateadjs:
        ballotsets = ballotsets_by_debate_id[da.debate_id]
        for ballotset in ballotsets:
            scoresheet = Scoresheet(ballotset.ballotsub, da.adjudicator, load=False)
            scoresheet.da = da
            scoresheet.POSITIONS = POSITIONS
            scoresheet.update_debateteams(debateteams_by_debate_id[da.debate_id])
            scoresheet.init_blank_buffer()

            ballotset._adjudicator_sheets[da.adjudicator] = scoresheet
            scoresheets_by_ballotsub_and_debateadj_id[(ballotset.ballotsub.id, da.id)] = scoresheet

    ssbas = SpeakerScoreByAdj.objects.filter(ballot_submission__in=ballotsubs).select_related('debate_team')
    for ssba in ssbas:
        scoresheet = scoresheets_by_ballotsub_and_debateadj_id[(ssba.ballot_submission_id, ssba.debate_adjudicator_id)]
        scoresheet._set_score(ssba.debate_team, ssba.position, ssba.score)

    # Finally, check that everything is in order
    # ------------------------------------------
    for ballotsub in ballotsubs:
        ballotsub.ballot_set.assert_loaded()
