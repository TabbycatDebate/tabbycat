import json

from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib import messages
from django.db.models import Count

import motions.statistics as motion_statistics
from motions.models import Motion
from participants.models import Speaker, Team
from results.models import SpeakerScore, TeamScore
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin, TournamentMixin
from tournaments.models import Round
from utils.mixins import SuperuserRequiredMixin, VueTableTemplateView
from utils.tables import TabbycatTableBuilder

from .diversity import get_diversity_data_sets
from .teams import TeamStandingsGenerator
from .speakers import SpeakerStandingsGenerator
from .round_results import add_speaker_round_results, add_team_round_results, add_team_round_results_public
from .templatetags.standingsformat import metricformat


class StandingsIndexView(SuperuserRequiredMixin, RoundMixin, TemplateView):

    template_name = 'standings_index.html'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        round = self.get_round()

        speaks = SpeakerScore.objects.filter(
                    ballot_submission__confirmed=True, ghost=False,
                    speaker__team__tournament=t).exclude(
                    position=t.REPLY_POSITION).select_related(
                    'debate_team__debate__round')
        kwargs["top_speaks"] = speaks.order_by('-score')[:10]
        kwargs["bottom_speaks"] = speaks.order_by('score')[:10]

        margins = TeamScore.objects.filter(
                    ballot_submission__confirmed=True,
                    debate_team__team__tournament=t,
                    margin__gte=0).select_related(
                    'debate_team__team', 'debate_team__debate__round',
                    'debate_team__team__institution')
        kwargs["top_margins"] = margins.order_by('-margin')[:10]
        kwargs["bottom_margins"] = margins.order_by('margin')[:10]

        motions = Motion.objects.filter(
                    round__seq__lte=round.seq, round__tournament=t).annotate(
                    Count('ballotsubmission'))
        kwargs["top_motions"] = motions.order_by('-ballotsubmission__count')[:10]
        kwargs["bottom_motions"] = motions.order_by('ballotsubmission__count')[:10]

        return super().get_context_data(**kwargs)


# ==============================================================================
# Shared standings
# ==============================================================================

class BaseStandingsView(RoundMixin, VueTableTemplateView):

    def get_rounds(self):
        """Returns all of the rounds that should be included in the tab."""
        return self.get_tournament().prelim_rounds(until=self.get_round()).order_by('seq')


class PublicTabMixin(PublicTournamentPageMixin):
    """Mixin for views that should only be allowed when the tab is released publicly."""
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get_round(self):
        # Always show tabs with respect to current round on public tab pages,
        # or the last non-silent round if the current round is silent.
        tournament = self.get_tournament()
        round = tournament.current_round
        if round.silent and not tournament.pref('all_results_released'):
            round = tournament.prelim_rounds(until=round).filter(
                    silent=False).order_by('seq').last()
        return round

    def get_rounds(self):
        # Hide silent rounds
        rounds = super().get_rounds()
        if not self.get_tournament().pref('all_results_released'):
            rounds = rounds.filter(silent=False)
        return rounds

    def populate_result_missing(self, standings):
        # Never highlight missing results on public tab pages
        pass


# ==============================================================================
# Speaker standings
# ==============================================================================

class BaseSpeakerStandingsView(BaseStandingsView):
    """Base class for views that display speaker standings."""

    rankings = ('rank',)

    def get_standings(self):
        round = self.get_round()

        speakers = self.get_speakers()
        metrics, extra_metrics = self.get_metrics()
        rank_filter = self.get_rank_filter()
        generator = SpeakerStandingsGenerator(metrics, self.rankings,
                                              extra_metrics,
                                              rank_filter=rank_filter)
        standings = generator.generate(speakers, round=round)

        rounds = self.get_rounds()
        self.add_round_results(standings, rounds)
        self.populate_result_missing(standings)

        return standings, rounds

    def get_table(self):
        standings, rounds = self.get_standings()
        table = TabbycatTableBuilder(view=self, sort_key="Rk")

        # Easiest to redact info here before passing to column constructors
        for info in standings:
            info.speaker.anonymise = info.speaker.anonymous if self.public_page_preference else False
            info.speaker.team.anonymise = info.speaker.anonymous if self.public_page_preference else False

        table.add_ranking_columns(standings)
        table.add_speaker_columns([info.speaker for info in standings])
        table.add_team_columns([info.speaker.team for info in standings])

        scores_headers = [round.abbreviation for round in rounds]
        scores_data = [list(map(metricformat, standing.scores)) for standing in standings]
        table.add_columns(scores_headers, scores_data)
        table.add_metric_columns(standings)

        return table

    def get_rank_filter(self):
        return None

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.scores) > 1 and info.scores[-1] is None


class BaseStandardSpeakerStandingsView(BaseSpeakerStandingsView):
    """The standard speaker standings view."""
    page_title = 'Speaker Tab'
    page_emoji = '💯'

    def get_speakers(self):
        return Speaker.objects.filter(team__tournament=self.get_tournament()).select_related(
            'team', 'team__institution', 'team__tournament').prefetch_related('team__speaker_set')

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
    template_name = 'standings_base.html'


class PublicSpeakerTabView(PublicTabMixin, BaseStandardSpeakerStandingsView):
    public_page_preference = 'speaker_tab_released'


class BaseNoviceStandingsView(BaseStandardSpeakerStandingsView):
    """Speaker standings view for novices."""
    page_title = 'Novice Speaker Standings'

    def get_speakers(self):
        return super().get_speakers().filter(novice=True)


class NoviceStandingsView(SuperuserRequiredMixin, BaseNoviceStandingsView):
    template_name = 'standings_base.html'


class PublicNoviceTabView(PublicTabMixin, BaseNoviceStandingsView):
    public_page_preference = 'novices_tab_released'


class BaseProStandingsView(BaseStandardSpeakerStandingsView):
    """Speaker standings view for non-novices (pro, varsity)."""

    page_title = 'Pros Speaker Standings'

    def get_speakers(self):
        return super().get_speakers().filter(novice=False)


class ProStandingsView(SuperuserRequiredMixin, BaseProStandingsView):
    template_name = 'standings_base.html'


class PublicProTabView(PublicTabMixin, BaseProStandingsView):
    public_page_preference = 'pros_tab_released'


class BaseReplyStandingsView(BaseSpeakerStandingsView):
    """Speaker standings view for replies."""
    page_title = 'Reply Speaker Standings'
    page_emoji = '💁'

    def get_speakers(self):
        tournament = self.get_tournament()
        return Speaker.objects.filter(
            team__tournament=tournament,
            speakerscore__position=tournament.REPLY_POSITION).select_related(
            'team', 'team__institution', 'team__tournament').prefetch_related(
            'team__speaker_set').distinct()

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
    template_name = 'standings_base.html'


class PublicReplyTabView(PublicTabMixin, BaseReplyStandingsView):
    public_page_preference = 'replies_tab_released'


# ==============================================================================
# Team standings
# ==============================================================================

class BaseTeamStandingsView(BaseStandingsView):
    """Base class for views that display team standings."""

    page_title = 'Team Standings'
    page_emoji = '👯'

    def get_standings(self):
        tournament = self.get_tournament()
        round = self.get_round()

        teams = tournament.team_set.exclude(type=Team.TYPE_BYE).select_related('institution').prefetch_related('speaker_set')
        metrics = tournament.pref('team_standings_precedence')
        extra_metrics = tournament.pref('team_standings_extra_metrics')
        generator = TeamStandingsGenerator(metrics, self.rankings, extra_metrics)
        standings = generator.generate(teams, round=round)

        rounds = self.get_rounds()
        add_team_round_results(standings, rounds)
        self.populate_result_missing(standings)

        return standings, rounds

    def get_table(self):
        standings, rounds = self.get_standings()

        table = TabbycatTableBuilder(view=self, sort_key="Rk")
        table.add_ranking_columns(standings)
        table.add_team_columns([info.team for info in standings],
            show_divisions=self.get_tournament().pref('enable_divisions'))

        table.add_standings_results_columns(standings, rounds, self.show_ballots())
        table.add_metric_columns(standings)

        return table

    def show_ballots(self):
        return False

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.round_results) > 1 and info.round_results[-1] is None


class TeamStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """The standard team standings view."""
    rankings = ('rank',)
    template_name = 'standings_base.html'


class DivisionStandingsView(SuperuserRequiredMixin, BaseTeamStandingsView):
    """Special team standings view that also shows rankings within divisions."""
    rankings = ('rank', 'division')
    page_title = 'Division Standings'
    page_emoji = '👯'
    template_name = 'standings_base.html'


class PublicTeamTabView(PublicTabMixin, BaseTeamStandingsView):
    """Public view for the team tab.
    The team tab is actually what is presented to an admin as "team standings".
    During the tournament, "public team standings" only shows wins and results.
    Once the tab is released, to the public the team standings are known as the
    "team tab"."""
    public_page_preference = 'team_tab_released'
    rankings = ('rank',)

    def show_ballots(self):
        return self.get_tournament().pref('ballots_released')


# ==============================================================================
# Motion standings
# ==============================================================================

class BaseMotionStandingsView(BaseStandingsView):

    page_title = 'Motions Tab'
    page_emoji = '💭'

    def get_rounds(self):
        """Returns all of the rounds that should be included in the tab."""
        return self.get_tournament().round_set.order_by('seq')

    def get_table(self):
        motions = motion_statistics.statistics(tournament=self.get_tournament(), rounds=self.get_rounds())
        table = TabbycatTableBuilder(view=self, sort_key="Order")

        table.add_round_column([motion.round for motion in motions])
        table.add_motion_column(motions, show_order=True)
        table.add_column("Selected", [motion.chosen_in for motion in motions])
        if self.get_tournament().pref('motion_vetoes_enabled'):
            table.add_column("Aff Vetoes", [motion.aff_vetoes for motion in motions])
            table.add_column("Neg Vetoes", [motion.neg_vetoes for motion in motions])
        table.add_column("Aff Wins", [motion.aff_wins for motion in motions])
        table.add_column("Neg Wins", [motion.neg_wins for motion in motions])
        return table


class MotionStandingsView(SuperuserRequiredMixin, BaseMotionStandingsView):
    template_name = 'standings_base.html'


class PublicMotionsTabView(PublicTabMixin, BaseMotionStandingsView):
    public_page_preference = 'motion_tab_released'

    def get_rounds(self):
        """Returns all of the rounds that should be included in the tab."""
        return self.get_tournament().round_set.order_by('seq')


# ==============================================================================
# Current team standings (win-loss records only)
# ==============================================================================

class PublicCurrentTeamStandingsView(PublicTournamentPageMixin, VueTableTemplateView):

    public_page_preference = 'public_team_standings'
    page_title = 'Current Team Standings'
    page_emoji = '🌟'

    def get_table(self):
        tournament = self.get_tournament()

        # Find the most recent non-silent preliminary round
        round = tournament.current_round if tournament.pref('all_results_released') else tournament.current_round.prev
        while round is not None and (round.silent or round.stage != Round.STAGE_PRELIMINARY):
            round = round.prev

        if round is None or round.silent:
            return TabbycatTableBuilder() # empty (as precaution)

        teams = tournament.team_set.prefetch_related('speaker_set').order_by(
                'institution__code', 'reference')  # Obscure true rankings, in case client disabled JavaScript
        rounds = tournament.prelim_rounds(until=round).filter(silent=False).order_by('seq')

        add_team_round_results_public(teams, rounds)

        # pre-sort, as Vue tables can't do two sort keys
        teams = sorted(teams, key=lambda t: (-t.wins, t.short_name))

        table = TabbycatTableBuilder(view=self, sort_order='desc')
        table.add_team_columns(teams)
        table.add_column("Wins", [team.wins for team in teams])
        table.add_team_results_columns(teams, rounds)

        messages.info(self.request, "This list is sorted by wins, and then by "
            "team name within each group — it does not indicate each team's "
            "ranking within each group.")

        return table


# ==============================================================================
# Diversity
# ==============================================================================

class BaseDiversityStandingsView(TournamentMixin, TemplateView):

    template_name = 'diversity.html'
    for_public = False

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        all_data = get_diversity_data_sets(tournament, self.for_public)
        kwargs['regions'] = all_data['regions']
        kwargs['data_sets'] = json.dumps(all_data)
        kwargs['for_public'] = self.for_public
        return super().get_context_data(**kwargs)


class DiversityStandingsView(SuperuserRequiredMixin, BaseDiversityStandingsView):

    for_public = False


class PublicDiversityStandingsView(PublicTournamentPageMixin, BaseDiversityStandingsView):

    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT
    public_page_preference = 'public_diversity'
    for_public = True
