import json

from django.db.models import Count
from django.views.generic.base import ContextMixin, TemplateView, View
from django.conf import settings
from django.shortcuts import render

import motions.statistics as motion_statistics
from motions.models import Motion
from participants.models import Speaker, Team
from results.models import SpeakerScore, TeamScore
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin, TournamentMixin
from tournaments.models import Round
from utils.mixins import SuperuserRequiredMixin

from .diversity import get_diversity_data_sets
from .teams import TeamStandingsGenerator
from .speakers import SpeakerStandingsGenerator
from .round_results import add_speaker_round_results, add_team_round_results, add_team_round_results_public


class StandingsIndexView(SuperuserRequiredMixin, RoundMixin, TemplateView):

    template_name = 'standings_index.html'

    def get_context_data(self, **kwargs):
        round = self.get_round()

        speaks = SpeakerScore.objects.filter(ballot_submission__confirmed=True).exclude(
            position=round.tournament.REPLY_POSITION).select_related('debate_team__debate__round')
        kwargs["top_speaks"] = speaks.order_by('-score')[:10]
        kwargs["bottom_speaks"] = speaks.order_by('score')[:10]

        margins = TeamScore.objects.filter(
            ballot_submission__confirmed=True, margin__gte=0).select_related(
            'debate_team__team', 'debate_team__debate__round',
            'debate_team__team__institution')
        kwargs["top_margins"] = margins.order_by('-margin')[:10]
        kwargs["bottom_margins"] = margins.order_by('margin')[:10]

        motions = Motion.objects.filter(round__seq__lte=round.seq).annotate(
            Count('ballotsubmission'))
        kwargs["top_motions"] = motions.order_by('-ballotsubmission__count')[:10]
        kwargs["bottom_motions"] = motions.order_by('ballotsubmission__count')[:10]

        return super().get_context_data(**kwargs)


class PublicTabMixin(PublicTournamentPageMixin):
    """Mixin for views that should only be allowed when the tab is released publicly."""
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get_round(self):
        # Always show tabs with respect to current round on public tab pages
        return self.get_tournament().current_round

    def populate_result_missing(self, standings):
        # Never highlight missing results on public tab pages
        pass


# ==============================================================================
# Speaker standings
# ==============================================================================

class BaseSpeakerStandingsView(RoundMixin, ContextMixin, View):
    """Base class for views that display speaker standings."""

    rankings = ('rank',)

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        round = self.get_round()

        speakers = self.get_speakers()
        metrics, extra_metrics = self.get_metrics()
        rank_filter = self.get_rank_filter()
        generator = SpeakerStandingsGenerator(metrics, self.rankings,
                                              extra_metrics,
                                              rank_filter=rank_filter)
        standings = generator.generate(speakers, round=round)

        rounds = tournament.prelim_rounds(until=round).order_by('seq')
        self.add_round_results(standings, rounds)
        self.populate_result_missing(standings)
        context = self.get_context_data(standings=standings, rounds=rounds)

        return render(request, self.template_name, context)

    def get_rank_filter(self):
        return None

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.scores) > 1 and info.scores[-1] is None


class BaseStandardSpeakerStandingsView(BaseSpeakerStandingsView):
    """The standard speaker standings view."""

    def get_speakers(self):
        return Speaker.objects.filter(team__tournament=self.get_tournament()).select_related(
            'team', 'team__institution', 'team__tournament')

    def get_metrics(self):
        method = self.get_tournament().pref('rank_speakers_by')
        if method == 'average':
            return ('speaks_avg',), ('speaks_sum', 'speaks_stddev', 'speeches_count')
        else:
            return ('speaks_sum',), ('speaks_avg', 'speaks_stddev', 'speeches_count')

    def get_rank_filter(self):
        tournament = self.get_tournament()
        total_prelim_rounds = tournament.round_set.filter(
            stage=Round.STAGE_PRELIMINARY, seq__lte=self.get_round().seq).count()
        missable_debates = tournament.pref('standings_missed_debates')
        minimum_debates_needed = total_prelim_rounds - missable_debates
        return lambda info: info.metrics["speeches_count"] >= minimum_debates_needed

    def add_round_results(self, standings, rounds):
        add_speaker_round_results(standings, rounds, self.get_tournament())


class SpeakerStandingsView(SuperuserRequiredMixin, BaseStandardSpeakerStandingsView):
    template_name = 'speakers.html'


class PublicSpeakerTabView(PublicTabMixin, BaseStandardSpeakerStandingsView):
    public_page_preference = 'speaker_tab_released'
    template_name = 'public_speaker_tab.html'


class BaseNoviceStandingsView(BaseStandardSpeakerStandingsView):
    """Speaker standings view for novices."""

    template_name = 'novices.html'

    def get_speakers(self):
        return super().get_speakers().filter(novice=True)


class NoviceStandingsView(SuperuserRequiredMixin, BaseNoviceStandingsView):
    template_name = 'novices.html'


class PublicNoviceTabView(PublicTabMixin, BaseNoviceStandingsView):
    public_page_preference = 'novices_tab_released'
    template_name = 'public_novices_tab.html'


class BaseProStandingsView(BaseStandardSpeakerStandingsView):
    """Speaker standings view for non-novices (pro, varsity)."""

    def get_speakers(self):
        return super().get_speakers().filter(novice=False)


class ProStandingsView(SuperuserRequiredMixin, BaseProStandingsView):
    template_name = 'speakers.html'


class PublicProTabView(PublicTabMixin, BaseProStandingsView):
    public_page_preference = 'pros_tab_released'
    template_name = 'public_pros_tab.html'


class BaseReplyStandingsView(BaseSpeakerStandingsView):
    """Speaker standings view for replies."""

    def get_speakers(self):
        tournament = self.get_tournament()
        return Speaker.objects.filter(
            team__tournament=tournament,
            speakerscore__position=tournament.REPLY_POSITION).select_related(
            'team', 'team__institution', 'team__tournament').distinct()

    def get_metrics(self):
        return ('replies_avg',), ('replies_stddev', 'replies_count')

    def add_round_results(self, standings, rounds):
        add_speaker_round_results(standings, rounds, self.get_tournament(), replies=True)

    def populate_result_missing(self, standings):
        teams_seen = set()
        for info in standings:
            if len(info.scores) > 1 and info.scores[-1] is not None:
                teams_seen.add(info.speaker.team)

        for info in standings:
            info.result_missing = info.speaker.team not in teams_seen


class ReplyStandingsView(SuperuserRequiredMixin, BaseReplyStandingsView):
    template_name = 'replies.html'


class PublicReplyTabView(PublicTabMixin, BaseReplyStandingsView):
    public_page_preference = 'replies_tab_released'
    template_name = 'public_reply_tab.html'


# ==============================================================================
# Team standings
# ==============================================================================

class BaseTeamStandingsView(RoundMixin, ContextMixin, View):
    """Base class for views that display team standings."""

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

        teams = tournament.team_set.exclude(type=Team.TYPE_BYE).select_related('institution')
        metrics = tournament.pref('team_standings_precedence')
        extra_metrics = tournament.pref('team_standings_extra_metrics')
        generator = TeamStandingsGenerator(metrics, self.rankings, extra_metrics)
        standings = generator.generate(teams, round=round)

        rounds = tournament.prelim_rounds(until=round).order_by('seq')
        add_team_round_results(standings, rounds)
        self.populate_result_missing(standings)

        context = self.get_context_data(standings=standings, rounds=rounds)

        return render(request, self.template_name, context)

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.round_results) > 1 and info.round_results[-1] is None


class TeamStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """The standard team standings view."""
    rankings = ('rank',)
    template_name = 'teams.html'


class DivisionStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """Special team standings view that also shows rankings within divisions."""
    rankings = ('rank', 'division')
    template_name = 'divisions.html'


class PublicTeamTabView(PublicTabMixin, BaseTeamStandingsView):
    """Public view for the team tab.
    The team tab is actually what is presented to an admin as "team standings".
    During the tournament, "public team standings" only shows wins and results.
    Once the tab is released, to the public the team standings are known as the
    "team tab"."""
    public_page_preference = 'team_tab_released'
    rankings = ('rank',)
    template_name = 'public_team_tab.html'

    def show_ballots(self):
        return self.get_tournament().pref('ballots_released')


# ==============================================================================
# Motion standings
# ==============================================================================

class BaseMotionStandingsView(RoundMixin, TemplateView):

    def get_context_data(self, **kwargs):
        kwargs["motions"] = motion_statistics.statistics(round=self.get_round())
        return super().get_context_data(**kwargs)


class MotionStandingsView(SuperuserRequiredMixin, BaseMotionStandingsView):
    template_name = 'motions.html'


class PublicMotionsTabView(PublicTabMixin, BaseMotionStandingsView):
    public_page_preference = 'motion_tab_released'
    template_name = 'public_motions_tab.html'


# ==============================================================================
# Current team standings (win-loss records only)
# ==============================================================================

class PublicCurrentTeamStandingsView(PublicTournamentPageMixin, TemplateView):
    public_page_preference = 'public_team_standings'
    template_name = 'public_team_standings.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()

        # Find the most recent non-silent preliminary round
        round = tournament.current_round if tournament.release_all else tournament.current_round.prev
        while round is not None and (round.silent or round.stage != Round.STAGE_PRELIMINARY):
            round = round.prev

        if round is not None and round.silent is False:
            teams = tournament.team_set.order_by('institution__code', 'reference')  # Obscure true rankings, in case client disabled JavaScript
            rounds = tournament.prelim_rounds(until=round).filter(silent=False).order_by('seq')
            add_team_round_results_public(teams, rounds)

            kwargs["teams"] = teams
            kwargs["rounds"] = rounds
            kwargs["round"] = round
        else:
            kwargs["teams"] = []
            kwargs["rounds"] = []
            kwargs["round"] = None

        return super().get_context_data(**kwargs)


# ==============================================================================
# Diversity
# ==============================================================================

class BaseDiversityStandingsView(TournamentMixin, TemplateView):

    template_name = 'diversity.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        all_data = get_diversity_data_sets(tournament, self.for_public)
        kwargs['regions'] = all_data['regions']
        kwargs['data_sets'] = json.dumps(all_data)
        kwargs['for_public'] = self.for_public
        return super().get_context_data(**kwargs)


class DiversityStandingsView(BaseDiversityStandingsView, SuperuserRequiredMixin):

    for_public = False


class PublicDiversityStandingsView(BaseDiversityStandingsView, PublicTabMixin):

    public_page_preference = 'public_diversity'
    for_public = True
