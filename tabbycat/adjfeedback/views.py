import csv
import json
import logging
import math

from django.contrib import messages
from django.db.models import Count, F, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy, ngettext, ngettext_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from options.utils import use_team_code_names, use_team_code_names_data_entry
from participants.models import Adjudicator, Speaker, Team
from participants.prefetch import populate_feedback_scores
from participants.templatetags.team_name_for_data_entry import team_name_for_data_entry
from results.mixins import PublicSubmissionFieldsMixin, TabroomSubmissionFieldsMixin
from results.prefetch import populate_wins_for_debateteams
from tournaments.mixins import (PersonalizablePublicTournamentPageMixin, PublicTournamentPageMixin, SingleObjectByRandomisedUrlMixin,
                                SingleObjectFromTournamentMixin, TournamentMixin)
from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.tables import TabbycatTableBuilder
from utils.views import PostOnlyRedirectView, VueTableTemplateView

from .forms import make_feedback_form_class, UpdateAdjudicatorScoresForm
from .models import AdjudicatorBaseScoreHistory, AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from .prefetch import populate_debate_adjudicators
from .progress import get_feedback_progress
from .tables import FeedbackTableBuilder
from .utils import get_feedback_overview

logger = logging.getLogger(__name__)


class BaseFeedbackOverview(TournamentMixin, VueTableTemplateView):
    """ Also inherited by the adjudicator's tab """

    def get_adjudicators(self):
        if not hasattr(self, '_adjudicators'):
            t = self.tournament
            self._adjudicators = Adjudicator.objects.filter(tournament=t)
            populate_feedback_scores(self._adjudicators)
        return self._adjudicators

    def get_context_data(self, **kwargs):
        t = self.tournament
        adjudicators = self.get_adjudicators()
        weight = t.current_round.feedback_weight
        scores = [a.weighted_score(weight) for a in adjudicators]

        kwargs['c_breaking'] = adjudicators.filter(breaking=True).count()

        ntotal = len(scores)
        ntrainees = [x < t.pref('adj_min_voting_score') for x in scores].count(True)
        nvoting = ntotal - ntrainees
        ndebates = t.team_set.count() // (4 if t.pref('teams_in_debate') == 'bp' else 2)
        nchairs = min(nvoting, ndebates)
        npanellists = nvoting - nchairs

        max_score = int(math.ceil(t.pref('adj_max_score')))
        min_score = int(math.floor(t.pref('adj_min_score')))
        range_width = max_score - min_score
        band_widths = [range_width // 5] * 5
        for i in range(range_width - sum(band_widths)):
            band_widths[i] += 1
        band_widths = [x for x in band_widths if x > 0]
        bands = []
        threshold = max_score
        for width in band_widths:
            bands.append((threshold - width, threshold))
            threshold = threshold - width
        if not threshold == min_score:
            logger.error("Feedback bands calculation didn't work")

        band_specs = []
        threshold_classes = ['80', '70', '60', '50', '40'] # CSS suffix
        for (band_min, band_max), threshold_class in zip(bands, threshold_classes):
            band_specs.append({
                'min': band_min, 'max': band_max, 'class': threshold_class,
                'count': [x >= band_min and x < band_max for x in scores].count(True),
            })
        band_specs[0]['count'] += [x == max_score for x in scores].count(True)

        noutside_range = [x < min_score or x > max_score for x in scores].count(True)

        kwargs.update({
            'c_total': ntotal,
            'c_chairs': nchairs,
            'c_debates': ndebates,
            'c_panellists': npanellists,
            'c_trainees': ntrainees,
            'c_thresholds': band_specs,
            'nadjs_outside_range': noutside_range,
            'test_percent': (1.0 - weight) * 100,
            'feedback_percent': weight * 100,
        })

        return super().get_context_data(**kwargs)

    def get_table(self):
        t = self.tournament
        adjudicators = self.get_adjudicators()
        # Gather stats necessary to construct the graphs
        adjudicators = get_feedback_overview(t, adjudicators)
        table = FeedbackTableBuilder(view=self, sort_key=self.sort_key,
                                     sort_order=self.sort_order)
        table = self.annotate_table(table, adjudicators)
        return table


class FeedbackOverview(AdministratorMixin, BaseFeedbackOverview):

    page_title = gettext_lazy("Feedback Overview")
    page_emoji = '🙅'
    for_public = False
    sort_key = 'score'
    sort_order = 'desc'
    template_name = 'feedback_overview.html'

    def annotate_table(self, table, adjudicators):
        feedback_weight = self.tournament.current_round.feedback_weight
        scores = {adj: adj.weighted_score(feedback_weight) for adj in adjudicators}

        table.add_adjudicator_columns(adjudicators, show_institutions=False, subtext='institution')
        table.add_breaking_checkbox(adjudicators)
        table.add_weighted_score_columns(adjudicators, scores)
        table.add_base_score_columns(adjudicators, editable=True)
        table.add_score_difference_columns(adjudicators, scores)
        table.add_score_variance_columns(adjudicators)
        table.add_feedback_graphs(adjudicators)
        table.add_feedback_link_columns(adjudicators)
        return table


class FeedbackByTargetView(AdministratorMixin, TournamentMixin, VueTableTemplateView):
    template_name = "feedback_base.html"
    page_title = gettext_lazy("Find Feedback on Adjudicator")
    page_emoji = '🔍'

    def get_table(self):
        adjudicators = self.tournament.adjudicator_set.annotate(feedback_count=Count('adjudicatorfeedback'))
        table = TabbycatTableBuilder(view=self, sort_key="name")
        table.add_adjudicator_columns(adjudicators)
        feedback_data = []
        for adj in adjudicators:
            count = adj.feedback_count
            feedback_data.append({
                'text': ngettext("%(count)d feedback", "%(count)d feedbacks", count) % {'count': count},
                'link': reverse_tournament('adjfeedback-view-on-adjudicator', self.tournament, kwargs={'pk': adj.id}),
            })
        table.add_column({'key': 'feedbacks', 'title': _("Feedbacks")}, feedback_data)
        return table


class FeedbackBySourceView(AdministratorMixin, TournamentMixin, VueTableTemplateView):

    template_name = "feedback_base.html"
    page_title = gettext_lazy("Find Feedback")
    page_emoji = '🔍'

    def get_tables(self):
        tournament = self.tournament

        teams = tournament.team_set.all().annotate(feedback_count=Count('debateteam__adjudicatorfeedback')).prefetch_related('speaker_set')
        team_table = TabbycatTableBuilder(
            view=self, title=_('From Teams'), sort_key='team')
        team_table.add_team_columns(teams)
        team_feedback_data = []
        for team in teams:
            count = team.feedback_count
            team_feedback_data.append({
                'text': ngettext("%(count)d feedback", "%(count)d feedbacks", count) % {'count': count},
                'link': reverse_tournament('adjfeedback-view-from-team',
                                           tournament,
                                           kwargs={'pk': team.id}),
            })
        team_table.add_column({'key': 'feedbacks', 'title': _("Feedbacks")}, team_feedback_data)

        adjudicators = tournament.adjudicator_set.all().annotate(feedback_count=Count('debateadjudicator__adjudicatorfeedback'))
        adj_table = TabbycatTableBuilder(
            view=self, title=_('From Adjudicators'), sort_key='name')
        adj_table.add_adjudicator_columns(adjudicators)
        adj_feedback_data = []
        for adj in adjudicators:
            count = adj.feedback_count
            adj_feedback_data.append({
                'text': ngettext("%(count)d feedback", "%(count)d feedbacks", count) % {'count': count},
                'link': reverse_tournament('adjfeedback-view-from-adjudicator',
                                           tournament,
                                           kwargs={'pk': adj.id}),
            })
        adj_table.add_column({'key': 'feedbacks', 'title': _("Feedbacks")}, adj_feedback_data)

        return [team_table, adj_table]


class FeedbackMixin(TournamentMixin):
    only_comments = False

    def get_feedbacks(self):
        feedbacks = self.get_feedback_queryset()

        populate_debate_adjudicators(feedbacks)
        populate_wins_for_debateteams([f.source_team for f in feedbacks if f.source_team is not None])

        # Can't prefetch an abstract model effectively; so get all answers...
        questions = list(self.tournament.adj_feedback_questions)
        if self.only_comments:
            long_text = AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT
            questions = [q for q in questions if q.answer_type == long_text]

        for question in questions:
            question.answers = list(question.answer_set.values())

        for feedback in feedbacks:
            feedback.items = []
            # ...and stitch them together manually
            for question in questions:
                for answer in question.answers:
                    if answer['feedback_id'] == feedback.id:
                        feedback.items.append({'question': question,
                                               'answer': answer['answer']})
                        break # Should only be one match

        if self.only_comments:
            feedbacks = [f for f in feedbacks if len(f.items) > 0] # Remove null
        return feedbacks

    def get_feedback_queryset(self):
        return AdjudicatorFeedback.objects.filter(
            Q(adjudicator__tournament=self.tournament) |
            Q(adjudicator__tournament__isnull=True),
        ).select_related(
            'adjudicator',
            'source_adjudicator__adjudicator',
            'source_adjudicator__debate__round',
            'source_team__debate__round',
            'source_team__team',
            'source_team__team__tournament',
        )


class FeedbackCardsView(FeedbackMixin, AdministratorMixin, TournamentMixin, TemplateView):
    """Base class for views displaying feedback as cards."""
    template_name = "feedback_cards_list.html"

    def get_score_thresholds(self):
        tournament = self.tournament
        min_score = tournament.pref('adj_min_score')
        max_score = tournament.pref('adj_max_score')
        score_range = max_score - min_score
        return {
            'low_score'     : min_score + score_range / 10,
            'medium_score'  : min_score + score_range / 5,
            'high_score'    : max_score - score_range / 10,
        }

    def get_context_data(self, **kwargs):
        kwargs['feedbacks'] = self.get_feedbacks()
        kwargs['score_thresholds'] = self.get_score_thresholds()
        return super().get_context_data(**kwargs)


class LatestFeedbackView(FeedbackCardsView):
    """View displaying the latest feedback."""
    page_title = gettext_lazy("Latest Feedback")
    page_subtitle = gettext_lazy("(30 most recent)")
    page_emoji = '🕗'

    def get_feedback_queryset(self):
        queryset = super().get_feedback_queryset()
        return queryset.order_by('-timestamp')[:30]


class CommentsFeedbackView(FeedbackCardsView):
    """View displaying the latest feedback."""
    page_title = gettext_lazy("Only Comments")
    page_subtitle = gettext_lazy("(250 most recent)")
    page_emoji = '💬'
    only_comments = True

    def get_feedback_queryset(self):
        queryset = super().get_feedback_queryset()
        return queryset.order_by('-timestamp')[:250]


class ImportantFeedbackView(FeedbackCardsView):
    """View displaying the feedback in order of most 'important'."""
    page_title = gettext_lazy("Important Feedback")
    page_subtitle = gettext_lazy("(rating was much higher/lower than expected)")
    page_emoji = '⁉️'

    def get_feedback_queryset(self):
        queryset = super().get_feedback_queryset()
        return queryset.annotate(
            feedback_importance=F('score') - F('adjudicator__base_score'),
        ).filter(
            Q(feedback_importance__gt=2) | Q(feedback_importance__lt=-2),
        ).order_by('-timestamp')


class FeedbackFromSourceView(SingleObjectFromTournamentMixin, FeedbackCardsView):
    """Base class for views displaying feedback from a given team or adjudicator."""

    template_name = "feedback_by_source.html"
    source_name_attr = None
    source_type = "from"
    adjfeedback_filter_field = None

    def get_context_data(self, **kwargs):
        kwargs['source_name'] = getattr(self.object, self.source_name_attr, '<ERROR>')
        kwargs['source_type'] = self.source_type
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_feedback_queryset(self):
        queryset = super().get_feedback_queryset()
        kwargs = {self.adjfeedback_filter_field: self.object}
        return queryset.filter(**kwargs).order_by('-timestamp')


class FeedbackOnAdjudicatorView(FeedbackFromSourceView):
    """Base class for views displaying feedback from a given team or adjudicator."""

    model = Adjudicator
    source_name_attr = 'name'
    source_type = "on"
    adjfeedback_filter_field = 'adjudicator'
    allow_null_tournament = True


class FeedbackFromTeamView(FeedbackFromSourceView):
    """View displaying feedback from a given source."""
    model = Team
    source_name_attr = 'short_name'
    adjfeedback_filter_field = 'source_team__team'
    allow_null_tournament = False


class FeedbackFromAdjudicatorView(FeedbackFromSourceView):
    """View displaying feedback from a given adjudicator."""
    model = Adjudicator
    source_name_attr = 'name'
    adjfeedback_filter_field = 'source_adjudicator__adjudicator'
    allow_null_tournament = True


class BaseAddFeedbackIndexView(TournamentMixin, VueTableTemplateView):

    def get_tables(self):
        tournament = self.tournament

        use_code_names = use_team_code_names_data_entry(self.tournament, self.tabroom)
        teams_table = TabbycatTableBuilder(view=self, sort_key="team", title=_("A Team"))
        add_link_data = [{
            'text': team_name_for_data_entry(team, use_code_names),
            'link': self.get_from_team_link(team),
        } for team in tournament.team_set.all()]
        header = {'key': 'team', 'title': _("Team")}
        teams_table.add_column(header, add_link_data)

        if tournament.pref('show_team_institutions'):
            teams_table.add_column({
                'key': 'institution',
                'icon': 'home',
                'tooltip': _("Institution"),
            }, [team.institution.code if team.institution else TabbycatTableBuilder.BLANK_TEXT for team in tournament.team_set.all()])

        adjs_table = TabbycatTableBuilder(view=self, sort_key="adjudicator", title=_("An Adjudicator"))
        adjudicators = tournament.adjudicator_set.all()

        add_link_data = [{
            'text': adj.name,
            'link': self.get_from_adj_link(adj),
        } for adj in adjudicators]
        header = {'key': 'adjudicator', 'title': _("Adjudicator")}
        adjs_table.add_column(header, add_link_data)

        if tournament.pref('show_adjudicator_institutions'):
            adjs_table.add_column({
                'key': 'institution',
                'icon': 'home',
                'tooltip': _("Institution"),
            }, [adj.institution.code if adj.institution else TabbycatTableBuilder.BLANK_TEXT for adj in adjudicators])

        return [teams_table, adjs_table]


class AdminAddFeedbackIndexView(AdministratorMixin, BaseAddFeedbackIndexView):
    """View for the index page for administrators to add feedback. The index
    page lists all possible sources; officials should then choose the author
    of the feedback."""
    template_name = 'add_feedback.html'
    tabroom = True

    def get_from_adj_link(self, adj):
        return reverse_tournament('adjfeedback-add-from-adjudicator',
                self.tournament, kwargs={'source_id': adj.id})

    def get_from_team_link(self, team):
        return reverse_tournament('adjfeedback-add-from-team',
                self.tournament, kwargs={'source_id': team.id})


class AssistantAddFeedbackIndexView(AssistantMixin, BaseAddFeedbackIndexView):
    """As for AdminAddFeedbackIndexView, but for assistants."""
    template_name = 'assistant_add_feedback.html'
    tabroom = True

    def get_from_adj_link(self, adj):
        return reverse_tournament('adjfeedback-assistant-add-from-adjudicator',
                self.tournament, kwargs={'source_id': adj.id})

    def get_from_team_link(self, team):
        return reverse_tournament('adjfeedback-assistant-add-from-team',
                self.tournament, kwargs={'source_id': team.id})


class PublicAddFeedbackIndexView(PublicTournamentPageMixin, BaseAddFeedbackIndexView):
    """View for the index page for public users to add feedback. The index page
    lists all possible sources; public users should then choose themselves."""

    template_name = 'public_add_feedback.html'
    tabroom = False

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_feedback') == 'public'

    def get_from_adj_link(self, team):
        return reverse_tournament('adjfeedback-public-add-from-adjudicator-pk',
                self.tournament, kwargs={'source_id': team.id})

    def get_from_team_link(self, team):
        return reverse_tournament('adjfeedback-public-add-from-team-pk',
                self.tournament, kwargs={'source_id': team.id})


class BaseAddFeedbackView(LogActionMixin, SingleObjectFromTournamentMixin, FormView):
    """Base class for views that allow users to add feedback."""

    template_name = "enter_feedback.html"
    pk_url_kwarg = 'source_id'
    allow_null_tournament = True
    action_log_content_object_attr = 'adj_feedback'

    def get_form_class(self):
        return make_feedback_form_class(self.object, self.tournament,
                self.get_submitter_fields(), **self.feedback_form_class_kwargs)

    def form_valid(self, form):
        self.adj_feedback = form.save()
        self.round = self.adj_feedback.debate.round  # for LogActionMixin
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        source = self.object
        if isinstance(source, Adjudicator):
            kwargs['source_type'] = "adj"
        elif isinstance(source, Speaker):
            kwargs['source_type'] = "team"
        kwargs['source_name'] = self.source_name
        return super().get_context_data(**kwargs)

    def _populate_source(self):
        self.object = self.get_object()  # For compatibility with SingleObjectMixin
        if isinstance(self.object, Adjudicator):
            self.source_name = self.object.name
        elif isinstance(self.object, Speaker):
            self.source_name = self.get_team_short_name(self.object.team)
        elif isinstance(self.object, Team):
            self.source_name = self.get_team_short_name(self.object)
        else:
            logger.error("self.object was neither an Adjudicator nor a Speaker")
            self.source_name = "<ERROR>"

    def get(self, request, *args, **kwargs):
        self._populate_source()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._populate_source()
        return super().post(request, *args, **kwargs)


class BaseTabroomAddFeedbackView(TabroomSubmissionFieldsMixin, BaseAddFeedbackView):
    """View for tabroom officials to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SAVE
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': False,
        'include_unreleased_draws': True,
        'use_tournament_password': False,
        'ignored_option': True,
    }

    def get_team_short_name(self, team):
        use_code_names = use_team_code_names_data_entry(self.tournament, tabroom=True)
        return team_name_for_data_entry(team, use_code_names)

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, _("Feedback from %(source)s on %(target)s added.") % {
            'source': self.source_name, 'target': self.adj_feedback.adjudicator.name})
        return result

    def get_success_url(self):
        return reverse_tournament('adjfeedback-add-index', self.tournament)


class AdminAddFeedbackView(AdministratorMixin, BaseTabroomAddFeedbackView):
    pass


class AssistantAddFeedbackView(AssistantMixin, BaseTabroomAddFeedbackView):
    pass


class PublicAddFeedbackView(PublicSubmissionFieldsMixin, PersonalizablePublicTournamentPageMixin, BaseAddFeedbackView):
    """Base class for views for public users to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SUBMIT
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': True,
        'include_unreleased_draws': False,
        'use_tournament_password': True,
        'ignored_option': False,
    }

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, _("Thanks, %(source)s! Your feedback on %(target)s has been recorded.") % {
            'source': self.source_name, 'target': self.adj_feedback.adjudicator.name})
        return result

    def get_context_data(self, **kwargs):
        kwargs['no_rounds_released'] = not self.tournament.round_set.filter(
                draw_status=Round.STATUS_RELEASED).exists()
        return super().get_context_data(**kwargs)


class PublicAddFeedbackByRandomisedUrlView(SingleObjectByRandomisedUrlMixin, PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is a randomised one."""

    def get_team_short_name(self, team):
        # It's a private URL, so always show the team's real name.
        return team.short_name

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_feedback') == 'private-urls'

    def get_submitter_fields(self):
        fields = super().get_submitter_fields()
        fields['participant_submitter'] = self.object
        return fields

    def get_success_url(self):
        # Redirect to non-cached page: their original private URL
        if isinstance(self.object, Adjudicator):
            return reverse_tournament('adjfeedback-public-add-from-adjudicator-randomised',
                self.tournament, kwargs={'url_key': self.object.url_key})
        elif isinstance(self.object, Speaker):
            return reverse_tournament('adjfeedback-public-add-from-team-randomised',
                self.tournament, kwargs={'url_key': self.object.url_key})
        else:
            raise ValueError("Private feedback source is not of a valid type")


class SpeakerAddFeedbackByRandomisedUrlView(PublicAddFeedbackByRandomisedUrlView):
    model = Speaker
    tournament_field_name = 'team__tournament'


class AdjudicatorAddFeedbackByRandomisedUrlView(PublicAddFeedbackByRandomisedUrlView):
    model = Adjudicator


class PublicAddFeedbackByIdUrlView(PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is by object ID."""

    tabroom = False

    def get_team_short_name(self, team):
        use_code_names = use_team_code_names(self.tournament, admin=False)
        return team.code_name if use_code_names else team.short_name

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_feedback') == 'public'

    def get_success_url(self):
        # Redirect to non-cached page: the public feedback form
        if isinstance(self.object, Adjudicator):
            return reverse_tournament('adjfeedback-public-add-from-adjudicator-pk',
                self.tournament, kwargs={'source_id': self.object.id})
        elif isinstance(self.object, Team):
            return reverse_tournament('adjfeedback-public-add-from-team-pk',
                self.tournament, kwargs={'source_id': self.object.id})
        else:
            raise ValueError("Public feedback source is not of a valid type")


class AdjudicatorActionError(RuntimeError):
    pass


class BaseAdjudicatorActionView(LogActionMixin, AdministratorMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'adjfeedback-overview'
    action_log_content_object_attr = 'adjudicator'

    def get_adjudicator(self, request):
        try:
            adj_id = int(request.POST["adj_id"])
            adjudicator = Adjudicator.objects.get(id=adj_id)
        except (ValueError, Adjudicator.DoesNotExist, Adjudicator.MultipleObjectsReturned):
            raise AdjudicatorActionError(_("Whoops! I didn't recognise that adjudicator: %(adjudicator)s") % {'adjudicator': adj_id})
        return adjudicator

    def post(self, request, *args, **kwargs):
        try:
            self.adjudicator = self.get_adjudicator(request)
            self.modify_adjudicator(request, self.adjudicator)
            self.log_action()  # Need to call explicitly, since this isn't a form view
        except AdjudicatorActionError as e:
            messages.error(request, str(e))

        return super().post(request, *args, **kwargs)


class SetAdjudicatorBaseScoreView(BaseAdjudicatorActionView):

    action_log_type = ActionLogEntry.ACTION_TYPE_TEST_SCORE_EDIT
    action_log_content_object_attr = 'atsh'

    def modify_adjudicator(self, request, adjudicator):
        try:
            score = float(request.POST["base_score"])
        except ValueError:
            raise AdjudicatorActionError(_("Whoops! The value isn't a valid base score."))

        adjudicator.base_score = score
        adjudicator.save()

        atsh = AdjudicatorBaseScoreHistory(
            adjudicator=adjudicator, round=self.tournament.current_round,
            score=score)
        atsh.save()
        self.atsh = atsh


class SetAdjudicatorBreakingStatusView(AdministratorMixin, TournamentMixin, LogActionMixin, View):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATOR_BREAK_SET

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)
        adjudicator = Adjudicator.objects.get(id=posted_info['id'])
        adjudicator.breaking = posted_info['breaking']
        adjudicator.save()
        return JsonResponse(json.dumps(True), safe=False)


class BaseFeedbackProgressView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Feedback Progress")
    page_subtitle = ''
    page_emoji = '🆘'

    def get_feedback_progress(self):
        if not hasattr(self, "_feedback_progress_result"):
            self._feedback_progress_result = get_feedback_progress(self.tournament)
        return self._feedback_progress_result

    def get_page_subtitle(self):
        teams_progress, adjs_progress = self.get_feedback_progress()
        all_progress = teams_progress + adjs_progress
        total_missing = sum([progress.num_unsubmitted() for progress in all_progress])
        total_expected = sum([progress.num_expected() for progress in all_progress])

        try:
            percentage_fulfilled = (1 - total_missing / total_expected) * 100
        except ZeroDivisionError:
            percentage_fulfilled = 100

        return ngettext_lazy(
            "%(nmissing)d missing feedback submission (%(fulfilled).1f%% returned)",
            "%(nmissing)d missing feedback submissions (%(fulfilled).1f%% returned)",
            total_missing,
        ) % {'nmissing': total_missing, 'fulfilled': percentage_fulfilled}

    def get_tables(self):
        teams_progress, adjs_progress = self.get_feedback_progress()

        adjs_table = FeedbackTableBuilder(view=self, title=_("From Adjudicators"),
            sort_key="owed", sort_order="desc")
        adjudicators = [progress.adjudicator for progress in adjs_progress]
        adjs_table.add_adjudicator_columns(adjudicators, show_metadata=False)
        adjs_table.add_feedback_progress_columns(adjs_progress)

        teams_table = FeedbackTableBuilder(view=self, title=_("From Teams"),
            sort_key="owed", sort_order="desc")
        teams = [progress.team for progress in teams_progress]
        teams_table.add_team_columns(teams)
        teams_table.add_feedback_progress_columns(teams_progress)

        return [adjs_table, teams_table]


class FeedbackProgress(AdministratorMixin, BaseFeedbackProgressView):
    template_name = 'feedback_base.html'


class PublicFeedbackProgress(PublicTournamentPageMixin, BaseFeedbackProgressView):
    public_page_preference = 'feedback_progress'


class BaseFeedbackToggleView(AdministratorMixin, TournamentMixin, PostOnlyRedirectView):

    def post(self, request, *args, **kwargs):
        feedback = AdjudicatorFeedback.objects.get(id=kwargs['feedback_id'])
        feedback = self.modify_feedback(feedback)
        feedback.save()

        # Make message
        if feedback.source_adjudicator:
            source = feedback.source_adjudicator.adjudicator.name
        else:
            source = feedback.source_team.team.short_name
        result = self.feedback_result(feedback)
        messages.success(self.request, _(
            "Feedback for %(adjudicator)s from %(source)s is now %(result)s.")
            % {'adjudicator': feedback.adjudicator.name, 'source': source, 'result': result})

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        # Returns to the referring page (by way of hidden input with the path)
        fallback = reverse_tournament('adjfeedback-overview', self.tournament)
        return self.request.POST.get('next', fallback)


class ConfirmFeedbackView(BaseFeedbackToggleView):

    def feedback_result(self, feedback):
        return _("confirmed") if feedback.confirmed else _("un-confirmed")

    def modify_feedback(self, feedback):
        feedback.confirmed = not feedback.confirmed
        if feedback.confirmed:
            feedback.confirm_timestamp = timezone.now()
            feedback.confirmer = self.request.user
        return feedback


class IgnoreFeedbackView(BaseFeedbackToggleView):

    def feedback_result(self, feedback):
        return _("ignored") if feedback.ignored else _("un-ignored")

    def modify_feedback(self, feedback):
        feedback.ignored = not feedback.ignored
        return feedback


# ==============================================================================
# Update adjudicator scores in bulk
# ==============================================================================

class UpdateAdjudicatorScoresView(AdministratorMixin, LogActionMixin, TournamentMixin, FormView):
    template_name = 'update_adjudicator_scores.html'
    form_class = UpdateAdjudicatorScoresForm
    action_log_type = ActionLogEntry.ACTION_TYPE_UPDATE_ADJUDICATOR_SCORES

    def get_context_data(self, **kwargs):
        sample_adjs = self.tournament.relevant_adjudicators.all()[:3]
        if len(sample_adjs) == 0:
            kwargs['no_adjs_in_database'] = True
            kwargs['sample'] = [("Estella Brandybuck", 5.0), ("Pia Hermansson", 4.0), ("Lucas Sousa", 3.5)]
        else:
            kwargs['sample'] = [(adj.name, adj.base_score) for adj in sample_adjs]
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs

    def get_success_url(self):
        return reverse_tournament('adjfeedback-overview', self.tournament)

    def form_valid(self, form):
        nupdated = form.save()
        messages.success(self.request, ngettext(
            "Updated base score for %(count)d adjudicator.",
            "Updated base scores for %(count)d adjudicators.",
            nupdated) % {'count': nupdated})
        self.log_action()
        return super().form_valid(form)


# ==============================================================================
# CSV dumps
# ==============================================================================
# These are a stopgap while we develop a proper API for this.

class BaseCsvView(View):

    def get_filename(self):
        return self.filename

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=\"" + self.get_filename() + "\""

        writer = csv.writer(response)
        self.write_rows(writer)

        return response


class AdjudicatorScoresCsvView(TournamentMixin, AdministratorMixin, BaseCsvView):
    filename = "scores.csv"

    def write_rows(self, writer):
        writer.writerow(["id", "name", "base_score", "gender", "region", "nrounds"])
        for adj in self.tournament.adjudicator_set.all():
            row = [adj.id, adj.name, adj.base_score, adj.gender]
            row.append(adj.region.name if adj.region else "")
            row.append(adj.debateadjudicator_set.count())
            writer.writerow(row)


class AdjudicatorFeedbackCsvView(FeedbackMixin, AdministratorMixin, TournamentMixin, BaseCsvView):
    filename = "feedback.csv"

    def get_feedback_queryset(self):
        return super().get_feedback_queryset().filter(confirmed=True)

    def write_rows(self, writer):
        headers = [
            "round.seq", "round.abbreviation",
            "adjudicator.id", "adjudicator.name", "adjudicator.type",
            "source_adjudicator.id", "source_adjudicator.name", "source_adjudicator.type",
            "source_team.id", "source_team.short_name", "source_team.result",
            "score", "ignored",
        ]
        question_references = [q.reference for q in self.tournament.adj_feedback_questions]
        headers.extend(question_references)
        writer.writerow(headers)

        feedbacks = self.get_feedbacks()
        for f in feedbacks:
            row = [f.round.seq, f.round.abbreviation,
                f.adjudicator.id, f.adjudicator.name, f.debate_adjudicator.get_type_display()]

            if f.source_adjudicator:
                adj = f.source_adjudicator.adjudicator
                row.extend([adj.id, adj.name, f.source_adjudicator.get_type_display()])
            else:
                row.extend([""] * 3)

            if f.source_team:
                team = f.source_team.team
                row.extend([team.id, team.short_name, f.source_team.get_result_display()])
            else:
                row.extend([""] * 3)

            row.append(f.score)
            row.append(f.ignored)

            answers = {q['question'].reference: q['answer'] for q in f.items}
            row.extend([answers.get(ref, '') for ref in question_references])

            writer.writerow(row)
