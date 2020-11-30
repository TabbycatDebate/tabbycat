import json
import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import Avg, Count, Prefetch
from django.utils.html import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic.base import TemplateView

from adjfeedback.views import BaseFeedbackOverview
from breakqual.models import BreakCategory
from motions.models import Motion
from notifications.models import BulkNotification
from notifications.views import RoundTemplateEmailCreateView
from options.utils import use_team_code_names
from participants.models import Speaker, SpeakerCategory, Team
from results.models import SpeakerScore, TeamScore
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin, SingleObjectFromTournamentMixin, TournamentMixin
from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import VueTableTemplateView

from .base import StandingsError
from .diversity import get_diversity_data_sets
from .round_results import add_speaker_round_results, add_team_round_results, add_team_round_results_public
from .speakers import SpeakerStandingsGenerator
from .teams import TeamStandingsGenerator
from .templatetags.standingsformat import metricformat

logger = logging.getLogger(__name__)


class StandingsIndexView(AdministratorMixin, RoundMixin, TemplateView):

    template_name = 'standings_index.html'

    def get_context_data(self, **kwargs):
        speaks = SpeakerScore.objects.filter(
            ballot_submission__confirmed=True,
            ghost=False,
            speaker__team__tournament=self.tournament,
        ).exclude(
            position=self.tournament.reply_position,
        ).select_related('debate_team__debate__round')
        kwargs["top_speaks"] = speaks.order_by('-score')[:9]
        kwargs["bottom_speaks"] = speaks.order_by('score')[:9]

        overall = speaks.filter(
            debate_team__debate__round__stage=Round.STAGE_PRELIMINARY,
        ).aggregate(Avg('score'))['score__avg']
        kwargs["round_speaks"] = [{'round': 'Overall (for in-rounds)',
                                   'score': overall}]
        for r in self.tournament.round_set.order_by('seq'):
            avg = speaks.filter(debate_team__debate__round=r).aggregate(
                Avg('score'))['score__avg']
            if avg:
                kwargs["round_speaks"].append({'round': r.name, 'score': avg})

        team_scores = TeamScore.objects.filter(
            ballot_submission__confirmed=True,
            debate_team__team__tournament=self.tournament,
        ).select_related(
            'debate_team__team',
            'debate_team__debate__round',
            'debate_team__team__institution',
        )
        if self.tournament.pref('teams_in_debate') == 'bp':
            team_scores.filter(debate_team__debate__round__stage=Round.STAGE_PRELIMINARY)
            kwargs["top_team_scores"] = team_scores.order_by('-score')[:9]
            kwargs["bottom_team_scores"] = team_scores.order_by('score')[:9]
        else:
            team_scores = team_scores.filter(margin__gte=0)
            kwargs["top_margins"] = team_scores.order_by('-margin')[:9]
            kwargs["bottom_margins"] = team_scores.order_by('margin')[:9]

        if self.tournament.pref('motion_vetoes_enabled'):
            motions = Motion.objects.filter(
                round__seq__lte=self.round.seq,
                round__tournament=self.tournament,
            ).annotate(Count('ballotsubmission'))
            kwargs["top_motions"] = motions.order_by('-ballotsubmission__count')[:4]
            kwargs["bottom_motions"] = motions.order_by('ballotsubmission__count')[:4]

        return super().get_context_data(**kwargs)


# ==============================================================================
# Shared standings
# ==============================================================================

class BaseStandingsView(RoundMixin, VueTableTemplateView):

    template_name = 'standings_table.html'

    standings_error_message = gettext_lazy(
        "<p>There was an error generating the standings: "
        "<em>%(message)s</em></p>",
    )

    admin_standings_error_instructions = gettext_lazy(
        "<p>You may need to double-check the "
        "<a href=\"%(standings_options_url)s\" class=\"alert-link\">"
        "standings configuration under the Setup section</a>. "
        "If this issue persists and you're not sure how to fix it, please "
        "contact the developers.</p>",
    )

    public_standings_error_instructions = gettext_lazy(
        "<p>The tab director will need to resolve this issue.</p>",
    )

    def get_page_subtitle(self):
        return _("as of %(round)s") % {'round': self.round.name}

    def get_rounds(self):
        """Returns all of the rounds that should be included in the tab."""
        return self.tournament.prelim_rounds(until=self.round).order_by('seq')

    def get_standings_error_message(self, e):
        if self.request.user.is_superuser:
            instructions = self.admin_standings_error_instructions
        else:
            instructions = self.public_standings_error_instructions

        message = self.standings_error_message % {'message': str(e)}
        standings_options_url = reverse_tournament('options-tournament-section', self.tournament, kwargs={'section': 'standings'})
        instructions %= {'standings_options_url': standings_options_url}
        return mark_safe(message + instructions)


class PublicTabMixin(PublicTournamentPageMixin):
    """Mixin for views that should only be allowed when the tab is released publicly."""
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get_page_subtitle(self):
        return None

    @property
    def round(self):
        if hasattr(self, "_round"):
            return self._round

        # Always show tabs with respect to current round on public tab pages,
        # or the last non-silent round if the current round is silent.
        self._round = self.tournament.current_round
        if self._round.silent and not self.tournament.pref('all_results_released'):
            self._round = self.tournament.prelim_rounds(until=self._round).filter(
                    silent=False).order_by('seq').last()
        return self._round

    def get_rounds(self):
        # Hide silent rounds
        rounds = super().get_rounds()
        if not self.tournament.pref('all_results_released'):
            rounds = rounds.filter(silent=False)
        return rounds

    def get_tab_limit(self):
        if hasattr(self, 'public_limit_preference'):
            return self.tournament.pref(self.public_limit_preference)
        else:
            return None

    def limit_rank_display(self, standings):
        """Sets the rank limit on the generated standings."""
        limit = self.get_tab_limit()
        if limit:
            standings.set_rank_limit(limit)

    def populate_result_missing(self, standings):
        # Never highlight missing results on public tab pages
        pass

    def append_limit(self, title):
        limit = self.get_tab_limit()
        if limit:
            # Translators: 'title' is the main title; "(Top 15 Only)" is just a suffix
            return _("%(title)s (Top %(limit)d Only)") % {'title': title, 'limit': limit}
        else:
            return title

    def get_page_title(self):
        # If set, make a note of any rank limitations in the title
        title = super().get_page_title()
        return self.append_limit(title)

    def get_context_data(self, **kwargs):
        kwargs['for_public'] = True
        return super().get_context_data(**kwargs)


# ==============================================================================
# Speaker standings
# ==============================================================================

class BaseSpeakerStandingsView(BaseStandingsView):
    """Base class for views that display speaker standings."""

    rankings = ('rank',)

    def get_standings(self):
        if self.round is None:
            raise StandingsError(_("The tab can't be displayed because all rounds so far in this tournament are silent."))

        speakers = self.get_speakers()
        speakers = speakers.select_related(
            'team', 'team__institution', 'team__tournament',
        ).prefetch_related(
            'team__speaker_set', 'categories',
        )

        metrics, extra_metrics = self.get_metrics()
        rank_filter = self.get_rank_filter()
        generator = SpeakerStandingsGenerator(metrics, self.rankings, extra_metrics, rank_filter=rank_filter)
        standings = generator.generate(speakers, round=self.round)

        rounds = self.get_rounds()
        self.add_round_results(standings, rounds)
        self.populate_result_missing(standings)
        self.limit_rank_display(standings)

        return standings, rounds

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key="rk")

        try:
            standings, rounds = self.get_standings()
        except StandingsError as e:
            messages.error(self.request, self.get_standings_error_message(e))
            logger.exception("Error generating standings: " + str(e))
            return table

        # Easiest to redact info here before passing to column constructors
        if hasattr(self, 'public_page_preference'):
            for info in standings:
                if info.speaker.anonymous:
                    info.speaker.anonymise = True
                    info.speaker.team.anonymise = True

        table.add_ranking_columns(standings)
        table.add_speaker_columns([info.speaker for info in standings])
        table.add_team_columns([info.speaker.team for info in standings])

        scores_headers = [{'key': round.abbreviation, 'title': round.abbreviation} for round in rounds]
        scores_data = [[metricformat(x) if x is not None else '—' for x in standing.scores] for standing in standings]
        table.add_columns(scores_headers, scores_data)
        table.add_metric_columns(standings, integer_score_columns=self.integer_score_columns(rounds))

        return table

    def limit_rank_display(self, standings):
        # Only filter ranks on PublicTabMixin
        pass

    def integer_score_columns(self, rounds):
        # Only for substantive speech standings
        return []

    def get_rank_filter(self):
        return None

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.scores) > 1 and info.scores[-1] is None

    def cast_round_results(self, standings, rounds, step_preference):
        """For use by subclasses. Casts round results to integers if appropriate
        according to tournament preferences."""
        if self.tournament.pref(step_preference).is_integer():
            is_consensus_by_round = [self.tournament.ballots_per_debate(r.stage) == 'per-debate' for r in rounds]
            for info in standings:
                for i, is_consensus in enumerate(is_consensus_by_round):
                    if is_consensus and info.scores[i] is not None and info.scores[i].is_integer():
                        info.scores[i] = int(info.scores[i])


class BaseSubstantiveSpeakerStandingsView(BaseSpeakerStandingsView):
    page_title = gettext_lazy("Speaker Standings")
    page_emoji = '💯'

    def get_speakers(self):
        return Speaker.objects.filter(team__tournament=self.tournament)

    def get_metrics(self):
        metrics = self.tournament.pref('speaker_standings_precedence')
        extra_metrics = self.tournament.pref('speaker_standings_extra_metrics')

        # 'count' is necessary to enforce the 'missed debates' limit, so add it if necessary.
        # There's also an alert in the speaker_standings.html template to explain this.
        if self.tournament.pref('standings_missed_debates') >= 0 and 'count' not in metrics and 'count' not in extra_metrics:
            extra_metrics.append('count')

        return metrics, extra_metrics

    def integer_score_columns(self, rounds):
        if all(self.tournament.integer_scores(rd.stage) for rd in rounds):
            return ['total']
        else:
            return []

    def get_rank_filter(self):
        missable_debates = self.tournament.pref('standings_missed_debates')
        if missable_debates < 0:
            return None  # no limit
        total_prelim_rounds = self.tournament.round_set.filter(
            stage=Round.STAGE_PRELIMINARY, seq__lte=self.round.seq).count()
        minimum_debates_needed = total_prelim_rounds - missable_debates
        return lambda info: info.metrics["count"] >= minimum_debates_needed

    def add_round_results(self, standings, rounds):
        add_speaker_round_results(standings, rounds, self.tournament)
        self.cast_round_results(standings, rounds, 'score_step')


class SpeakerStandingsView(AdministratorMixin, BaseSubstantiveSpeakerStandingsView):
    template_name = 'speaker_standings.html'  # add info alerts


class PublicSpeakerTabView(PublicTabMixin, BaseSubstantiveSpeakerStandingsView):
    page_title = gettext_lazy("Speaker Tab")
    public_page_preference = 'speaker_tab_released'
    public_limit_preference = 'speaker_tab_limit'


class BaseSpeakerCategoryStandingsView(SingleObjectFromTournamentMixin, BaseSubstantiveSpeakerStandingsView):
    """Speaker standings view for a category."""

    model = SpeakerCategory
    slug_url_kwarg = 'category'

    def get_speakers(self):
        return self.object.speaker_set.all()

    def get_page_title(self):
        return _("%(category)s Speaker Standings") % {'category': self.object.name}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class SpeakerCategoryStandingsView(AdministratorMixin, BaseSpeakerCategoryStandingsView):
    pass


class PublicSpeakerCategoryTabView(PublicTabMixin, BaseSpeakerCategoryStandingsView):
    public_page_preference = 'speaker_category_tabs_released'

    def get_tab_limit(self):
        return self.object.limit

    def get_page_title(self):
        title = _("%(category)s Speaker Tab") % {'category': self.object.name}
        return self.append_limit(title)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.public:
            logger.warning("Tried to access a non-public speaker category tab page: %s", self.object.slug)
            return self.render_page_disabled_error_page()
        return super().get(request, *args, **kwargs)


class BaseReplyStandingsView(BaseSpeakerStandingsView):
    """Speaker standings view for replies."""
    page_title = gettext_lazy("Reply Speaker Standings")
    page_emoji = '💁'

    def get_speakers(self):
        if self.tournament.reply_position is None:
            raise StandingsError(_("Reply speeches aren't enabled in this tournament."))
        return Speaker.objects.filter(
            team__tournament=self.tournament,
            speakerscore__position=self.tournament.reply_position,
        ).distinct()

    def get_metrics(self):
        return ('replies_avg',), ('replies_stddev', 'replies_count')

    def get_rank_filter(self):
        missable_replies = self.tournament.pref('standings_missed_replies')
        if missable_replies < 0:
            return None  # no limit
        total_prelim_rounds = self.tournament.round_set.filter(
            stage=Round.STAGE_PRELIMINARY, seq__lte=self.round.seq).count()
        minimum_replies_needed = total_prelim_rounds - missable_replies
        return lambda info: info.metrics["replies_count"] >= minimum_replies_needed

    def add_round_results(self, standings, rounds):
        add_speaker_round_results(standings, rounds, self.tournament, replies=True)
        self.cast_round_results(standings, rounds, 'reply_score_step')

    def populate_result_missing(self, standings):
        teams_seen = set()
        for info in standings:
            if len(info.scores) > 1 and info.scores[-1] is not None:
                teams_seen.add(info.speaker.team)

        for info in standings:
            info.result_missing = info.speaker.team not in teams_seen


class ReplyStandingsView(AdministratorMixin, BaseReplyStandingsView):
    template_name = 'reply_standings.html'  # add an info alert


class PublicReplyTabView(PublicTabMixin, BaseReplyStandingsView):
    page_title = gettext_lazy("Reply Speaker Tab")
    public_page_preference = 'replies_tab_released'
    public_limit_preference = 'replies_tab_limit'


# ==============================================================================
# Team standings
# ==============================================================================

class BaseTeamStandingsView(BaseStandingsView):
    """Base class for views that display team standings."""

    page_title = gettext_lazy("Team Standings")
    page_emoji = '👯'

    def get_teams(self):
        return self.tournament.team_set.exclude(type=Team.TYPE_BYE)

    def get_standings(self):
        if self.round is None:
            raise StandingsError(_("The tab can't be displayed because all rounds so far in this tournament are silent."))

        teams = self.get_teams()
        teams = teams.select_related('institution').prefetch_related('speaker_set',
            Prefetch('break_categories',
                queryset=BreakCategory.objects.filter(is_general=False),
                to_attr='break_categories_nongeneral'))
        metrics = self.tournament.pref('team_standings_precedence')
        extra_metrics = self.tournament.pref('team_standings_extra_metrics')
        generator = TeamStandingsGenerator(metrics, self.rankings, extra_metrics)
        standings = generator.generate(teams, round=self.round)
        self.limit_rank_display(standings)

        rounds = self.get_rounds()
        opponents = self.tournament.pref('teams_in_debate') == 'two'
        add_team_round_results(standings, rounds, opponents=opponents)
        self.populate_result_missing(standings)

        return standings, rounds

    def limit_rank_display(self, standings):
        # Only filter ranks on PublicTabMixin
        pass

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key="rk")

        try:
            standings, rounds = self.get_standings()
        except StandingsError as e:
            messages.error(self.request, self.get_standings_error_message(e))
            logger.exception("Error generating standings: " + str(e))
            return table

        table.add_ranking_columns(standings)
        table.add_team_columns([info.team for info in standings], show_break_categories=True)

        table.add_standings_results_columns(standings, rounds, self.show_ballots())
        table.add_metric_columns(standings, integer_score_columns=self.integer_score_columns(rounds))

        return table

    def show_ballots(self):
        return False

    def integer_score_columns(self, rounds):
        if all(self.tournament.integer_scores(rd.stage) for rd in rounds):
            return ['speaks_sum']
        else:
            return []

    def populate_result_missing(self, standings):
        for info in standings:
            info.result_missing = len(info.round_results) > 1 and info.round_results[-1] is None


class TeamStandingsView(AdministratorMixin, BaseTeamStandingsView):
    """Superuser team standings view."""
    template_name = 'team_standings.html'  # add info alerts
    rankings = ('rank',)

    def show_ballots(self):
        return True


class PublicTeamTabView(PublicTabMixin, BaseTeamStandingsView):
    """Public view for the team tab.
    The team tab is actually what is presented to an admin as "team standings".
    During the tournament, "public team standings" only shows wins and results.
    Once the tab is released, to the public the team standings are known as the
    "team tab"."""
    page_title = gettext_lazy("Team Tab")
    public_page_preference = 'team_tab_released'
    public_limit_preference = 'team_tab_limit'
    rankings = ('rank',)

    def show_ballots(self):
        return self.tournament.pref('ballots_released')


class BaseBreakCategoryStandingsView(SingleObjectFromTournamentMixin, BaseTeamStandingsView):
    """Team standings view for a break category."""

    model = BreakCategory
    slug_url_kwarg = 'category'

    def get_teams(self):
        return self.object.team_set.all()

    def get_page_title(self):
        return _("%(category)s Team Standings") % {'category': self.object.name}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class BreakCategoryStandingsView(AdministratorMixin, BaseBreakCategoryStandingsView):
    """Superuser team standings view for a break category."""
    rankings = ('rank',)

    def show_ballots(self):
        return True


class PublicBreakCategoryTabView(PublicTabMixin, BaseBreakCategoryStandingsView):
    """Public view for the team tab for a break category."""
    public_page_preference = 'break_category_tabs_released'
    rankings = ('rank',)

    def show_ballots(self):
        return self.tournament.pref('ballots_released')

    def get_tab_limit(self):
        return self.object.limit

    def get_page_title(self):
        title = _("%(category)s Team Tab") % {'category': self.object.name}
        return self.append_limit(title)


# ==============================================================================
# Current team standings (win-loss records only)
# ==============================================================================

class PublicCurrentTeamStandingsView(PublicTournamentPageMixin, VueTableTemplateView):

    public_page_preference = 'public_team_standings'
    page_title = gettext_lazy("Current Team Standings")
    page_emoji = '🌟'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT

    def get_rounds(self):
        if not hasattr(self, '_rounds'):
            if self.tournament.pref('all_results_released'):
                self._rounds = self.tournament.prelim_rounds().order_by('seq')
            else:
                self._rounds = self.tournament.prelim_rounds(before=self.tournament.current_round).filter(
                        silent=False).order_by('seq')
        return self._rounds

    def get_template_names(self):
        if not self.get_rounds():
            return ['current_standings_no_round.html']
        else:
            return ['current_standings.html']

    def get_table(self):
        rounds = self.get_rounds()
        if not rounds:
            return TabbycatTableBuilder(view=self) # empty (as precaution)

        name_attr = 'code_name' if use_team_code_names(self.tournament, False) else 'short_name'

        # Obscure true rankings, in case client disabled JavaScript
        teams = self.tournament.team_set.prefetch_related('speaker_set').order_by(name_attr)

        # Can't use prefetch.populate_win_counts, since that doesn't exclude
        # silent rounds and future rounds appropriately
        opponents = self.tournament.pref('teams_in_debate') == 'two'
        add_team_round_results_public(teams, rounds, opponents=opponents)

        # Pre-sort, as Vue tables can't do two sort keys
        teams = sorted(teams, key=lambda t: (-t.points, getattr(t, name_attr)))
        key, title = ('points', _("Points")) if self.tournament.pref('teams_in_debate') == 'bp' else ('wins', _("Wins"))
        header = {'key': key, 'tooltip': title, 'icon': 'bar-chart'}

        table = TabbycatTableBuilder(view=self, sort_order='desc')
        table.add_team_columns(teams)
        table.add_column(header, [team.points for team in teams])
        table.add_team_results_columns(teams, rounds)

        return table


# ==============================================================================
# Diversity
# ==============================================================================

class BaseDiversityStandingsView(TournamentMixin, TemplateView):

    template_name = 'standings_diversity.html'
    for_public = False

    def get_context_data(self, **kwargs):
        all_data = get_diversity_data_sets(self.tournament, self.for_public)
        kwargs['regions'] = all_data['regions']
        kwargs['data_sets'] = json.dumps(all_data)
        kwargs['for_public'] = self.for_public
        return super().get_context_data(**kwargs)


class DiversityStandingsView(AdministratorMixin, BaseDiversityStandingsView):

    for_public = False


class PublicDiversityStandingsView(PublicTournamentPageMixin, BaseDiversityStandingsView):

    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT
    public_page_preference = 'public_diversity'
    for_public = True


# ==============================================================================
# Adjudication
# ==============================================================================

class PublicAdjudicatorsTabView(PublicTabMixin, BaseFeedbackOverview):
    public_page_preference = 'adjudicators_tab_released'
    page_title = gettext_lazy('Feedback Overview')
    page_emoji = '🙅'
    for_public = False
    sort_key = 'name'
    sort_order = 'asc'
    template_name = 'standings_adjudicators.html'

    def annotate_table(self, table, adjudicators):
        table.add_adjudicator_columns(adjudicators)
        if self.tournament.pref('adjudicators_tab_shows') == 'final' or self.tournament.pref('adjudicators_tab_shows') == 'all':
            feedback_weight = self.tournament.current_round.feedback_weight
            scores = {adj: adj.weighted_score(feedback_weight) for adj in adjudicators}
            table.add_weighted_score_columns(adjudicators, scores)
        if self.tournament.pref('adjudicators_tab_shows') == 'test' or self.tournament.pref('adjudicators_tab_shows') == 'all':
            table.add_base_score_columns(adjudicators)
        if self.tournament.pref('adjudicators_tab_shows') == 'all':
            table.add_feedback_graphs(adjudicators)
        messages.info(self.request, _("An adjudicator's score is determined by "
            "a customisable mix of their base score and their feedback ratings."
            " The current mix is specified below as the 'Score Components.' "
            "Feedback ratings are determined by averaging the results of all "
            "individual pieces of feedback across all rounds. "
            "<a href='http://tabbycat.readthedocs.io/en/stable/features/adjudicator-feedback.html#how-is-an-adjudicator-s-score-determined'>Read more</a>."))
        return table


# ==============================================================================
# Send Emails
# ==============================================================================

class EmailTeamStandingsView(RoundTemplateEmailCreateView):
    page_subtitle = _("Team Standings")

    event = BulkNotification.EVENT_TYPE_POINTS
    subject_template = 'team_points_email_subject'
    message_template = 'team_points_email_message'

    round_redirect_pattern_name = 'tournament-complete-round-check'

    def get_queryset(self):
        return Speaker.objects.filter(team__tournament=self.tournament)

    def get_default_send_queryset(self):
        return Speaker.objects.filter(team__round_availabilities__round=self.round, email__isnull=False).exclude(email__exact="")

    def get_extra(self):
        extra = super().get_extra()
        if self.tournament.pref('public_team_standings'):
            extra['url'] = self.request.build_absolute_uri(reverse_tournament('standings-public-teams-current', self.tournament))
        else:
            extra['url'] = ""
        return extra
