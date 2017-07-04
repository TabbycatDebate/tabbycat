"""Functions that prefetch data for efficiency."""

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam
from tournaments.models import Tournament

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore
from .result import DebateResult


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

    teamscores = TeamScore.objects.filter(debate_team__debate__in=debates, ballot_submission__confirmed=True)
    teamscores_by_debateteam_id = {teamscore.debate_team_id: teamscore for teamscore in teamscores}

    for debateteam in debateteams:
        teamscore = teamscores_by_debateteam_id.get(debateteam.id, None)
        if teamscore is not None:
            debateteam._win = teamscore.win
        else:
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
    confirmed_ballots = BallotSubmission.objects.filter(debate__in=debates, confirmed=True)
    if motions:
        confirmed_ballots = confirmed_ballots.select_related('motion')
    if results:
        confirmed_ballots = confirmed_ballots.select_related(
            'debate__round__tournament').prefetch_related(
            'debate__debateadjudicator_set__adjudicator')

    ballotsubs_by_debate_id = {ballotsub.debate_id: ballotsub for ballotsub in confirmed_ballots}
    for debate in debates:
        debate._confirmed_ballot = ballotsubs_by_debate_id.get(debate.id, None)

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
        result = DebateResult(ballotsub, load=False)
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

        if not result.is_voting:
            result.set_score(ss.debate_team.side, ss.position, ss.score)

    # Populate scoresheets (load_scoresheets)

    if result.is_voting:

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
