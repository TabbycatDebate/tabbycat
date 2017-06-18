"""Functions that prefetch data for efficiency."""

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam
from tournaments.models import Tournament

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore
from .result import VotingDebateResult


def populate_wins(debates):
    """Sets an attribute `_win` on each DebateTeam in each Debate, representing
    whether they won the debate. For best results, the caller should already
    have had
        Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team'))
    prefetched on the query set.

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


def populate_confirmed_ballots(debates, motions=False, results=False):
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
    if results:
        confirmed_ballots = confirmed_ballots.select_related(
            'debate__round__tournament').prefetch_related(
            'debate__debateadjudicator_set__adjudicator')

    for ballotsub in confirmed_ballots:
        debate = debates_by_id[ballotsub.debate_id]
        debate._confirmed_ballot = ballotsub

    # populate the attribute for Debates that don't have a confirmed ballot
    for debate in debates:
        if not hasattr(debate, "_confirmed_ballot"):
            debate._confirmed_ballot = None

    if results:
        populate_results(confirmed_ballots)


def populate_results(ballotsubs):
    """Populates the `_result` attribute of each BallotSubmission in
    `ballotsubs` with a populated VotingDebateResult instance.

    For best performance, the ballot submissions should already have their
    debates prefetched (using select_related).
    """

    if not ballotsubs:
        return

    positions = Tournament.objects.get(round__debate__ballotsubmission=ballotsubs[0]).positions
    sides = ['aff', 'neg']
    ballotsubs = list(ballotsubs)  # set ballotsubs in stone to avoid race conditions in later queries

    results_by_debate_id = {}
    results_by_ballotsub_id = {}

    # Create the VotingDebateResults
    for ballotsub in ballotsubs:
        result = VotingDebateResult(ballotsub, load=False)
        result.init_blank_buffer()

        ballotsub._result = result
        results_by_debate_id.setdefault(ballotsub.debate_id, []).append(result)
        results_by_ballotsub_id[ballotsub.id] = result

    # Populate debateteams (load_debateteams)
    debateteams = DebateTeam.objects.filter(
        debate__ballotsubmission__in=ballotsubs,
        side__in=sides
    ).select_related('team').distinct()

    for dt in debateteams:
        for result in results_by_debate_id[dt.debate_id]:
            result.debateteams[dt.side] = dt

    # Populate speaker positions (load_speakers)
    speakerscores = SpeakerScore.objects.filter(
        ballot_submission__in=ballotsubs,
        debate_team__side__in=sides,
        position__in=positions
    ).select_related('debate_team')

    for ss in speakerscores:
        result = results_by_ballotsub_id[ss.ballot_submission_id]
        result.speakers[ss.debate_team.side][ss.position] = ss.speaker
        result.ghosts[ss.debate_team.side][ss.position] = ss.ghost

    # Populate scoresheets (load_scoresheets)

    debateadjs = DebateAdjudicator.objects.filter(
        debate__ballotsubmission__in=ballotsubs
    ).exclude(
        type=DebateAdjudicator.TYPE_TRAINEE
    ).select_related('adjudicator').distinct()

    for da in debateadjs:
        for result in results_by_debate_id[da.debate_id]:
            result.debateadjs[da.adjudicator] = da
            result.scoresheets[da.adjudicator] = result.scoresheet_class(positions)

    ssbas = SpeakerScoreByAdj.objects.filter(
        ballot_submission__in=ballotsubs,
        debate_team__side__in=sides,
        position__in=positions
    ).select_related('debate_adjudicator__adjudicator')

    for ssba in ssbas:
        result = results_by_ballotsub_id[ssba.ballot_submission_id]
        result.set_score(ssba.debate_adjudicator.adjudicator, ssba.debate_team.side,
            ssba.position, ssba.score)

    # Finally, check that everything is in order

    for ballotsub in ballotsubs:
        ballotsub.result.assert_loaded()
