"""Functions that prefetch data for efficiency."""
from itertools import groupby

from adjallocation.models import DebateAdjudicator
from checkins.utils import get_checkins
from draw.models import DebateTeam
from tournaments.models import Tournament

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore, TeamScoreByAdj
from .result import DebateResult, is_integer_step


def populate_wins(debates):
    """Sets the attributes `_win` and `_points` on each DebateTeam in each
    Debate, representing whether they won the debate and how many points they
    got from it. For best results, the caller should already have had
    Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team'))
    prefetched on the query set.

    This can be used for efficiency, since it retrieves all the
    information in bulk in a single SQL query. Operates in-place.
    """
    debateteams = [dt for debate in debates for dt in debate.debateteam_set.all()]
    populate_wins_for_debateteams(debateteams)


def populate_wins_for_debateteams(debateteams):

    teamscores = TeamScore.objects.filter(debate_team__in=debateteams, ballot_submission__confirmed=True)
    teamscores_by_debateteam_id = {teamscore.debate_team_id: teamscore for teamscore in teamscores}

    for debateteam in debateteams:
        teamscore = teamscores_by_debateteam_id.get(debateteam.id, None)
        if teamscore is not None:
            debateteam._win = teamscore.win
            debateteam._points = teamscore.points
        else:
            debateteam._win = None
            debateteam._points = None


def populate_confirmed_ballots(debates, motions=False, results=False):
    """Sets an attribute `_confirmed_ballot` on each Debate, each being the
    BallotSubmission instance for that debate.

    All the debates are assumed to be from the same tournament as the first.

    This can be used for efficiency, since it retrieves all the
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
            'debate__debateadjudicator_set__adjudicator__institution')

    ballotsubs_by_debate_id = {ballotsub.debate_id: ballotsub for ballotsub in confirmed_ballots}
    for debate in debates:
        debate._confirmed_ballot = ballotsubs_by_debate_id.get(debate.id, None)

    if results:
        populate_results(confirmed_ballots)


def populate_checkins(debates, tournament):
    get_checkins(debates, tournament, None)


def populate_results(ballotsubs, tournament=None):
    """Populates the `_result` attribute of each BallotSubmission in
    `ballotsubs` with a populated DebateResult instance.

    For best performance, the ballot submissions should already have their
    debates prefetched (using select_related).
    """

    # If the database is correct, some checks like `result.is_voting`,
    # `result.uses_speakers` etc. should be redundant. But it's best not to
    # assume this, so we always check these before calling a method that only
    # exists in some DebateResult subclasses.

    if not ballotsubs:
        return

    if tournament is None:
        tournament = Tournament.objects.get(round__debate__ballotsubmission=ballotsubs[0])
    positions = tournament.positions
    ballotsubs = list(ballotsubs)  # set ballotsubs in stone to avoid race conditions in later queries

    results_by_debate_id = {}
    results_by_ballotsub_id = {}

    debateteams = DebateTeam.objects.filter(
        debate__ballotsubmission__in=ballotsubs,
    ).select_related('team', 'team__tournament').order_by('debate_id').distinct()
    nsides_per_debate = {d_id: max([dt.side for dt in dts]) + 1 for d_id, dts in groupby(debateteams, key=lambda dt: dt.debate_id)}
    criteria = tournament.scorecriterion_set.all()

    # Create the DebateResults
    for ballotsub in ballotsubs:
        result = DebateResult(ballotsub, load=False, sides=range(nsides_per_debate.get(ballotsub.debate_id, tournament.pref('teams_in_debate'))), criteria=criteria)
        result.init_blank_buffer()

        ballotsub._result = result
        results_by_debate_id.setdefault(ballotsub.debate_id, []).append(result)
        results_by_ballotsub_id[ballotsub.id] = result

    # Populate debateteams (load_debateteams)
    for dt in debateteams:
        for result in results_by_debate_id[dt.debate_id]:
            result.debateteams[dt.side] = dt

    # Populate speaker positions (load_speakers)
    speakerscores = SpeakerScore.objects.filter(
        ballot_submission__in=ballotsubs,
        position__in=positions,
    ).select_related('speaker', 'speaker__team__tournament', 'debate_team').prefetch_related('speakercriterionscore_set__criterion')

    for ss in speakerscores:
        result = results_by_ballotsub_id[ss.ballot_submission_id]
        if result.uses_speakers:
            result.speakers[ss.debate_team.side][ss.position] = ss.speaker
            result.ghosts[ss.debate_team.side][ss.position] = ss.ghost

            if not result.is_voting:
                int_step = is_integer_step(tournament, ss)
                if len(ss.speakercriterionscore_set.all()) > 0:
                    for criterion_score in ss.speakercriterionscore_set.all():
                        score = criterion_score.score
                        score = int(score) if int_step and int(score) == score else score
                        result.set_criterion_score(ss.debate_team.side, ss.position, criterion_score.criterion, score)
                else:
                    result.set_score(ss.debate_team.side, ss.position, int(ss.score) if int_step and ss.score % 1 == 0 else ss.score)
                    result.set_speaker_rank(ss.debate_team.side, ss.position, ss.rank)

    # Populate scoresheets (load_scoresheets)
    debateadjs = DebateAdjudicator.objects.filter(
        debate__ballotsubmission__in=ballotsubs,
    ).exclude(
        type=DebateAdjudicator.TYPE_TRAINEE,
    ).select_related('adjudicator__institution', 'adjudicator__tournament').distinct()

    for da in debateadjs:
        for result in results_by_debate_id[da.debate_id]:
            if result.is_voting:
                result.debateadjs[da.adjudicator] = da
                result.scoresheets[da.adjudicator] = result.scoresheet_class(positions, sides=range(nsides_per_debate[da.debate_id]), criteria=criteria)

    ssbas = SpeakerScoreByAdj.objects.filter(
        ballot_submission__in=ballotsubs,
        position__in=positions,
    ).select_related('debate_adjudicator__adjudicator__institution', 'debate_team').prefetch_related('speakercriterionscorebyadj_set__criterion')

    for ssba in ssbas:
        result = results_by_ballotsub_id[ssba.ballot_submission_id]
        int_step = is_integer_step(tournament, ssba)
        if result.uses_speakers and result.is_voting:
            if len(ssba.speakercriterionscorebyadj_set.all()) > 0:
                for criterion_score in ssba.speakercriterionscorebyadj_set.all():
                    score = criterion_score.score
                    score = int(criterion_score.score) if int_step and criterion_score.score % 1 == 0 else score
                    result.set_criterion_score(ssba.debate_adjudicator.adjudicator, ssba.debate_team.side, ssba.position, criterion_score.criterion, score)
            else:
                result.set_score(ssba.debate_adjudicator.adjudicator, ssba.debate_team.side,
                    ssba.position, int(ssba.score) if int_step and ssba.score % 1 == 0 else ssba.score)

    # Populate advancing (load_advancing)
    teamscores = TeamScore.objects.filter(
        ballot_submission__in=ballotsubs,
    ).select_related('debate_team')

    for ts in teamscores:
        result = results_by_ballotsub_id[ts.ballot_submission_id]
        if result.uses_declared_winners and ts.win and not result.is_voting:
            result.add_winner(ts.debate_team.side)

    # Populate advancing (load_advancing)
    teamscoresbyadj = TeamScoreByAdj.objects.filter(
        ballot_submission__in=ballotsubs,
    ).select_related('debate_team')

    for tsba in teamscoresbyadj:
        result = results_by_ballotsub_id[tsba.ballot_submission_id]
        if result.uses_declared_winners and tsba.win:
            result.add_winner(tsba.debate_adjudicator.adjudicator, tsba.debate_team.side)

    # Finally, check that everything is in order

    for ballotsub in ballotsubs:
        ballotsub.result.assert_loaded()
