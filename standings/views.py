from django.db.models import Count
from django.views.generic.base import View, ContextMixin

from motions.models import Motion
from participants.models import Team, Speaker
from results.models import TeamScore, SpeakerScore, BallotSubmission
from tournaments.mixins import RoundMixin, PublicTournamentPageMixin
from tournaments.models import Round
from utils.mixins import SuperuserRequiredMixin
from utils.views import *

from .teams import TeamStandingsGenerator
from .round_results import add_team_round_results

@admin_required
@round_view
def standings_index(request, round):
    top_speaks = SpeakerScore.objects.filter(
        ballot_submission__confirmed=True).select_related(
            'debate_team__debate__round').order_by('-score')[:10]
    bottom_speaks = SpeakerScore.objects.filter(
        ballot_submission__confirmed=True).exclude(
            position=round.tournament.REPLY_POSITION).order_by(
                'score')[:10].select_related('debate_team__debate__round')
    top_margins = TeamScore.objects.filter(
        ballot_submission__confirmed=True).select_related(
            'debate_team__team', 'debate_team__debate__round',
            'debate_team__team__institution').order_by('-margin')[:10]
    bottom_margins = TeamScore.objects.filter(
        ballot_submission__confirmed=True, margin__gte=0).select_related(
            'debate_team__team', 'debate_team__debate__round',
            'debate_team__team__institution').order_by('margin')[:10]

    top_motions = Motion.objects.filter(round__seq__lte=round.seq).annotate(
        Count('ballotsubmission')).order_by('-ballotsubmission__count')[:10]
    bottom_motions = Motion.objects.filter(round__seq__lte=round.seq).annotate(
        Count('ballotsubmission')).order_by('ballotsubmission__count')[:10]

    return render(request,
               'standings_index.html',
               dict(top_margins=top_margins,
                    top_speaks=top_speaks,
                    bottom_margins=bottom_margins,
                    bottom_speaks=bottom_speaks,
                    top_motions=top_motions,
                    bottom_motions=bottom_motions))


def get_speaker_standings(rounds,
                          round,
                          results_override=False,
                          only_novices=False,
                          only_pros=False,
                          for_replies=False):
    last_substantive_position = round.tournament.LAST_SUBSTANTIVE_POSITION
    reply_position = round.tournament.REPLY_POSITION
    total_prelim_rounds = Round.objects.filter(
        stage=Round.STAGE_PRELIMINARY,
        tournament=round.tournament).count()
    missable_debates = round.tournament.pref('standings_missed_debates')
    minimum_debates_needed = total_prelim_rounds - missable_debates

    if for_replies:
        speaker_scores = SpeakerScore.objects.select_related(
            'speaker', 'ballot_submission',
            'debate_team__debate__round').filter(
                ballot_submission__confirmed=True,
                position=reply_position)
    else:
        speaker_scores = SpeakerScore.objects.select_related(
            'speaker', 'ballot_submission',
            'debate_team__debate__round').filter(
                ballot_submission__confirmed=True,
                position__lte=last_substantive_position)

    if only_novices is True:
        speakers = list(Speaker.objects.filter(
            team__tournament=round.tournament,
            novice=True).select_related('team', 'team__institution',
                                        'team__tournament'))
    elif only_pros is True:
        speakers = list(Speaker.objects.filter(
            team__tournament=round.tournament,
            novice=False).select_related('team', 'team__institution',
                                        'team__tournament'))
    else:
        speakers = list(Speaker.objects.filter(
            team__tournament=round.tournament).select_related(
                'team', 'team__institution', 'team__tournament'))

    def get_scores(speaker, this_speakers_scores):
        speaker_scores = [None] * len(rounds)
        for r in rounds:
            finding_score = next(
                (x
                 for x in this_speakers_scores
                 if x.debate_team.debate.round == r), None)
            if finding_score:
                speaker_scores[r.seq - 1] = finding_score.score

        return speaker_scores

    for speaker in speakers:
        this_speakers_scores = [score
                                for score in speaker_scores
                                if score.speaker == speaker]
        speaker.scores = get_scores(speaker, this_speakers_scores)
        speaker.results_in = speaker.scores[
            -
            1] is not None or round.stage != Round.STAGE_PRELIMINARY or results_override

        if round.seq < total_prelim_rounds or len(
            [_f for _f in speaker.scores if _f]) >= minimum_debates_needed:
            speaker.total = sum([_f for _f in speaker.scores if _f])
            try:
                speaker.average = sum([_f for _f in speaker.scores if _f
                                       ]) / len(
                                           [_f for _f in speaker.scores if _f])
            except ZeroDivisionError:
                speaker.average = 0.0
        else:
            speaker.total = 0.0
            speaker.average = 0.0

        if for_replies:
            speaker.replies_given = len([_f for _f in speaker.scores if _f])

    if for_replies:
        speakers = [s for s in speakers if s.replies_given > 0]

    prev_total = None
    current_rank = 0

    if for_replies or round.tournament.pref('rank_speakers_by') == 'average':
        method = False
        speakers.sort(key=lambda x: x.average, reverse=True)
    else:
        method = True
        speakers.sort(key=lambda x: x.total, reverse=True)

    for i, speaker in enumerate(speakers, start=1):
        if method:
            comparison = speaker.total
        else:
            comparison = speaker.average

        if comparison != prev_total:
            current_rank = i
            prev_total = comparison
        speaker.rank = current_rank

    return speakers




class BaseTeamStandingsView(RoundMixin, ContextMixin, View):
    """Base class for views that display team standings."""

    template_name = 'teams.html'

    def get_context_data(self, **kwargs):
        if 'show_ballots' not in kwargs:
            kwargs['show_ballots'] = self.show_ballots()
        if 'round' not in kwargs:
            kwargs['round'] = self.get_round()
        return super().get_context_data(**kwargs)

    def show_ballots(self):
        return False

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        round = self.get_round()

        teams = Team.objects.teams_for_standings(round)
        metrics = tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics, self.rankings)
        standings = generator.generate(teams, round=round)

        rounds = tournament.prelim_rounds(until=round).order_by('seq')
        add_team_round_results(standings, rounds, (lambda standings, x: standings.get_standing(x)))

        context = self.get_context_data(standings=standings, rounds=rounds)

        return render(request, self.template_name, context)


class TeamStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """The standard team standings view."""
    rankings = ('rank',)


class DivisionStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """Special team standings view that also shows rankings within divisions."""
    rankings = ('rank', 'division')

    template_name = 'divisions.html'

class PublicTabMixin(PublicTournamentPageMixin):
    """Mixin for views that should only be allowed when the tab is released publicly."""
    public_page_preference = 'team_tab_released'
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get_round(self):
        return self.get_tournament().current_round


class PublicTeamTabView(PublicTabMixin, BaseTeamStandingsView):
    """Public view for the team tab.
    The team tab is actually what is presented to an admin as "team standings".
    During the tournament, "public team standings" only shows wins and results.
    Once the tab is released, to the public the team standings are known as the
    "team tab"."""
    rankings = ('rank',)
    template_name = 'public_team_tab.html'

    def show_ballots(self):
        return self.get_tournament().pref('ballots_released')


@admin_required
@round_view
def speaker_standings(request, round):
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round)
    return render(request, 'speakers.html', dict(speakers=speakers,
                    rounds=rounds))


@admin_required
@round_view
def novice_standings(request, round):
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, only_novices=True)
    return render(request, "novices.html", dict(speakers=speakers,
                                        rounds=rounds))


@admin_required
@round_view
def pro_standings(request, round):
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, only_pros=True)
    return render(request, "novices.html", dict(speakers=speakers,
                                        rounds=rounds))

@admin_required
@round_view
def reply_standings(request, round):
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, for_replies=True)
    return render(request, 'replies.html', dict(speakers=speakers,
                                        rounds=rounds))

@admin_required
@round_view
def motion_standings(request, round):
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    motions = list()
    motions = Motion.objects.statistics(round=round)
    return render(request, 'motions.html', dict(motions=motions))


@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@public_optional_tournament_view('speaker_tab_released')
def public_speaker_tab(request, t):
    print("Generating public speaker tab")
    round = t.current_round
    rounds = t.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round)
    return render(request, 'public_speaker_tab.html', dict(speakers=speakers,
            rounds=rounds, round=round))


@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@public_optional_tournament_view('pros_tab_released')
def public_pros_tab(request, t):
    round = t.current_round
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, only_pros=True)
    return render(request, 'public_pros_tab.html', dict(speakers=speakers,
            rounds=rounds, round=round))

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@public_optional_tournament_view('novices_tab_released')
def public_novices_tab(request, t):
    round = t.current_round
    rounds = round.tournament.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, only_novices=True)
    return render(request, 'public_novices_tab.html', dict(speakers=speakers,
            rounds=rounds, round=round))


@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@public_optional_tournament_view('replies_tab_released')
def public_replies_tab(request, t):
    round = t.current_round
    rounds = t.prelim_rounds(until=round).order_by('seq')
    speakers = get_speaker_standings(rounds, round, for_replies=True)
    return render(request, 'public_reply_tab.html', dict(speakers=speakers,
            rounds=rounds, round=round))

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@public_optional_tournament_view('motion_tab_released')
def public_motions_tab(request, t):
    round = t.current_round
    rounds = t.prelim_rounds(until=round).order_by('seq')
    print(rounds)
    motions = list()
    motions = Motion.objects.statistics(round=round)
    return render(request, 'public_motions_tab.html', dict(motions=motions))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_team_standings')
def public_team_standings(request, t):
    print("Generating public team standings")
    if t.release_all:
        # Assume that the time "release all" is used, the current round
        # is the last round.
        round = t.current_round
    else:
        round = t.current_round.prev

    # Find the most recent non-silent preliminary round
    while round is not None and (round.silent or round.stage != Round.STAGE_PRELIMINARY):
        round = round.prev

    if round is not None and round.silent is False:

        from results.models import TeamScore

        # Ranking by institution__name and reference isn't the same as ordering by
        # short_name, which is what we really want. But we can't rank by short_name,
        # because it's not a field (it's a property). So we'll do this in JavaScript.
        # The real purpose of this ordering is to obscure the *true* ranking of teams
        # - teams are not supposed to know rankings between teams on the same number
        # of wins.
        teams = Team.objects.order_by('institution__code', 'reference')
        rounds = t.prelim_rounds(until=round).filter(silent=False).order_by('seq')

        add_team_round_results(teams, rounds, (lambda teams, x: [t for t in teams if t == x][0]))

        # Do this manually, in case there are silent rounds
        for team in teams:
            team.wins = [ts.win for ts in team.round_results if ts].count(True)
            team.points = sum([ts.points for ts in team.round_results if ts])

        return render(request, 'public_team_standings.html', dict(teams=teams, rounds=rounds, round=round))
    else:
        return render(request, 'index.html')
