import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from participants.models import Adjudicator, Team
from results.mixins import TabroomSubmissionFieldsMixin, PublicSubmissionFieldsMixin
from results.models import SpeakerScoreByAdj
from tournaments.mixins import TournamentMixin, PublicTournamentPageMixin
from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.mixins import SingleObjectFromTournamentMixin, SingleObjectByRandomisedUrlMixin, PublicCacheMixin
from utils.mixins import SuperuserRequiredMixin, SuperuserOrTabroomAssistantTemplateResponseMixin, PostOnlyRedirectView
from utils.urlkeys import populate_url_keys
from utils.views import *

from .models import AdjudicatorFeedback, AdjudicatorTestScoreHistory
from .forms import make_feedback_form_class
from .utils import gather_adj_feedback, gather_adj_scores


@admin_required
@tournament_view
def adj_scores(request, t):
    data = {}
    # TODO: make round-dependent
    for adj in Adjudicator.objects.all().select_related('tournament','tournament__current_round'):
        data[adj.id] = adj.score

    return HttpResponse(json.dumps(data), content_type="text/json")


@admin_required
@tournament_view
def feedback_overview(request, t):
    breaking_count = 0

    if t.pref('share_adjs'):
        adjudicators = Adjudicator.objects.filter(tournament=t).select_related(
            'tournament', 'tournament__current_round') | Adjudicator.objects.filter(tournament=None)
    else:
        adjudicators = Adjudicator.objects.filter(tournament=t).select_related(
            'tournament', 'tournament__current_round')

    all_debate_adjudicators = list(DebateAdjudicator.objects.select_related('adjudicator').all())

    all_adj_feedbacks = list(
        AdjudicatorFeedback.objects.filter(confirmed=True).exclude(
            source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE).select_related(
                'adjudicator', 'source_adjudicator__debate__round', 'source_team__debate__round'))

    all_adj_scores = list(
        SpeakerScoreByAdj.objects.select_related('debate_adjudicator', 'ballot_submission').filter(
            ballot_submission__confirmed=True))

    feedback_data = {}
    for adj in adjudicators:
        if adj.breaking:
            breaking_count += 1
        # Gather feedback scores for graphs
        adj_feedbacks = [f for f in all_adj_feedbacks if f.adjudicator == adj]
        feedback_data[adj.id] = gather_adj_feedback(adj, t.prelim_rounds(until=t.current_round), adj_feedbacks, all_debate_adjudicators)
        # Gather awarded scores for stats
        debate_adjudications = [a for a in all_debate_adjudicators if a.adjudicator.id is adj.id]
        scores = [s for s in all_adj_scores if s.debate_adjudicator.id is adj.id]
        adj = gather_adj_scores(adj, scores, debate_adjudications)

    context = {
        'adjudicators'      : adjudicators,
        'breaking_count'    : breaking_count,
        'feedback_headings' : [q.name for q in t.adj_feedback_questions],
        'feedback_data'     : json.dumps(feedback_data),
    }
    return render(request, 'feedback_overview.html', context)


class FeedbackBySourceView(LoginRequiredMixin, TournamentMixin, TemplateView):

    template_name = "adjudicator_source_list.html"

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        teams_data = []
        for team in Team.objects.filter(tournament=tournament):
            feedbacks = AdjudicatorFeedback.objects.filter(source_team__team=team).select_related(
                'source_team__team').count()
            teams_data.append({
                'name': team.short_name,
                'institution': team.institution.name,
                'feedbacks': "%s Feedbacks" % feedbacks,
                'rowLink': reverse_tournament('adjfeedback-view-from-team', tournament, kwargs={'pk': team.pk}),
            })

        adjs_data = []
        for adj in Adjudicator.objects.filter(tournament=tournament):
            feedbacks = AdjudicatorFeedback.objects.filter(
                source_adjudicator__adjudicator=adj).select_related(
                'source_adjudicator__adjudicator').count(),
            adjs_data.append({
                'name': adj.name,
                'institution': adj.institution.name,
                'feedbacks': "%s Feedbacks" % feedbacks,
                'rowLink': reverse_tournament('adjfeedback-view-from-adjudicator', tournament, kwargs={'pk': adj.pk}),
            })
        kwargs['teams'] = teams_data
        kwargs['adjs'] = adjs_data
        return super().get_context_data(**kwargs)


class FeedbackCardsView(LoginRequiredMixin, TournamentMixin, TemplateView):
    """Base class for views displaying feedback as cards."""

    def get_score_thresholds(self):
        tournament = self.get_tournament()
        min_score = tournament.pref('adj_min_score')
        max_score = tournament.pref('adj_max_score')
        score_range = max_score - min_score
        return {
            'low_score'     : min_score + score_range / 10,
            'medium_score'  : min_score + score_range / 5,
            'high_score'    : max_score - score_range / 10,
        }

    def get_feedbacks(self):
        questions = self.get_tournament().adj_feedback_questions
        feedbacks = self.get_feedback_queryset()
        for feedback in feedbacks:
            feedback.items = []
            for question in questions:
                try:
                    answer = question.answer_set.get(feedback=feedback).answer
                except ObjectDoesNotExist:
                    continue
                feedback.items.append({'question': question, 'answer': answer})
        return feedbacks

    def get_feedback_queryset(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        kwargs['feedbacks'] = self.get_feedbacks()
        kwargs['score_thresholds'] = self.get_score_thresholds()
        return super().get_context_data(**kwargs)


class LatestFeedbackView(FeedbackCardsView):
    """View displaying the latest feedback."""

    template_name = "feedback_latest.html"

    def get_feedback_queryset(self):
        return AdjudicatorFeedback.objects.order_by('-timestamp')[:50].select_related(
            'adjudicator', 'source_adjudicator__adjudicator', 'source_team__team')


class FeedbackFromSourceView(SingleObjectMixin, FeedbackCardsView):
    """Base class for views displaying feedback from a given team or adjudicator."""
    # SingleObjectFromTournamentMixin doesn't work great here, it induces an MRO
    # conflict between TournamentMixin and ContextMixin.

    template_name = "feedback_by_source.html"
    source_name_attr = None
    adjfeedback_filter_field = None

    def get_context_data(self, **kwargs):
        kwargs['source_name'] = getattr(self.object, self.source_name_attr, '<ERROR>')
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # from SingleObjectFromTournamentMixin
        return super().get_queryset().filter(tournament=self.get_tournament())

    def get_feedback_queryset(self):
        kwargs = {self.adjfeedback_filter_field: self.object}
        return AdjudicatorFeedback.objects.filter(**kwargs).order_by('-timestamp')


class FeedbackFromTeamView(FeedbackFromSourceView):
    """View displaying feedback from a given source."""
    model = Team
    source_name_attr = 'short_name'
    adjfeedback_filter_field = 'source_team__team'


class FeedbackFromAdjudicatorView(FeedbackFromSourceView):
    """View displaying feedback from a given adjudicator."""
    model = Adjudicator
    source_name_attr = 'name'
    adjfeedback_filter_field = 'source_adjudicator__adjudicator'


@login_required
@tournament_view
def get_adj_feedback(request, t):

    adj = get_object_or_404(Adjudicator, pk=int(request.GET['id']))
    feedback = adj.get_feedback().filter(confirmed=True)
    questions = t.adj_feedback_questions

    def _parse_feedback(f):

        if f.source_team:
            source_annotation = " (" + f.source_team.result + ")"
        elif f.source_adjudicator:
            source_annotation = " (" + f.source_adjudicator.get_type_display() + ")"
        else:
            source_annotation = ""

        data = [
            str(f.round.abbreviation),
            str(str(f.version) + (f.confirmed and "*" or "")),
            f.debate.bracket,
            f.debate.matchup,
            str(str(f.source) + source_annotation),
            f.score,
        ]
        for question in questions:
            try:
                data.append(question.answer_set.get(feedback=f).answer)
            except ObjectDoesNotExist:
                data.append("-")
        data.append(f.confirmed)
        return data
    data = [_parse_feedback(f) for f in feedback]
    return HttpResponse(json.dumps({'aaData': data}), content_type="text/json")


class BaseAddFeedbackIndexView(TournamentMixin, TemplateView):

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['adjudicators'] = tournament.adjudicator_set.all() if not tournament.pref('share_adjs') \
            else Adjudicator.objects.all()
        kwargs['teams'] = tournament.team_set.all()
        return super().get_context_data(**kwargs)


class TabroomAddFeedbackIndexView(SuperuserOrTabroomAssistantTemplateResponseMixin, BaseAddFeedbackIndexView):
    """View for the index page for tabroom officials to add feedback. The index
    page lists all possible sources; officials should then choose the author
    of the feedback."""

    superuser_template_name = 'add_feedback.html'
    assistant_template_name = 'assistant_add_feedback.html'


class PublicAddFeedbackIndexView(PublicCacheMixin, PublicTournamentPageMixin, BaseAddFeedbackIndexView):
    """View for the index page for public users to add feedback. The index page
    lists all possible sources; public users should then choose themselves."""

    template_name = 'public_add_feedback.html'
    public_page_preference = 'public_feedback'


class BaseAddFeedbackView(LogActionMixin, SingleObjectFromTournamentMixin, FormView):
    """Base class for views that allow users to add feedback.
    Subclasses must also subclass SingleObjectMixin, directly or indirectly."""

    template_name = "enter_feedback.html"
    pk_url_kwarg = 'source_id'

    def get_form_class(self):
        return make_feedback_form_class(
            self.object, self.get_submitter_fields(), **self.feedback_form_class_kwargs)

    def get_action_log_fields(self, **kwargs):
        kwargs['adjudicator_feedback'] = self.adj_feedback
        return super().get_action_log_fields(**kwargs)

    def form_valid(self, form):
        self.adj_feedback = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        source = self.object
        if isinstance(source, Adjudicator):
            kwargs['source_type'] = "adj"
        elif isinstance(source, Team):
            kwargs['source_type'] = "team"
        kwargs['source_name'] = self.source_name
        return super().get_context_data(**kwargs)

    def _populate_source(self):
        self.object = self.get_object()  # For compatibility with SingleObjectMixin
        if isinstance(self.object, Adjudicator):
            self.source_name = self.object.name
        elif isinstance(self.object, Team):
            self.source_name = self.object.short_name
        else:
            self.source_name = "<ERROR>"

    def get(self, request, *args, **kwargs):
        self._populate_source()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._populate_source()
        return super().post(request, *args, **kwargs)


class TabroomAddFeedbackView(TabroomSubmissionFieldsMixin, LoginRequiredMixin, BaseAddFeedbackView):
    """View for tabroom officials to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SAVE
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': False,
        'include_unreleased_draws': True,
    }

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, "Feedback from {} on {} added.".format(
            self.source_name, self.adj_feedback.adjudicator.name))
        return result

    def get_success_url(self):
        return reverse_tournament('adjfeedback-add-index', self.get_tournament())


class PublicAddFeedbackView(PublicSubmissionFieldsMixin, PublicTournamentPageMixin, BaseAddFeedbackView):
    """Base class for views for public users to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SUBMIT
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': True,
        'include_unreleased_draws': False,
    }

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, "Thanks, your feedback on has been recorded.")
        return result

    def get_success_url(self):
        return reverse_tournament('tournament-public-index', self.get_tournament())


class PublicAddFeedbackByRandomisedUrlView(SingleObjectByRandomisedUrlMixin, PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is a randomised one."""
    public_page_preference = 'public_feedback_randomised'


class PublicAddFeedbackByIdUrlView(PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is by object ID."""
    public_page_preference = 'public_feedback'


class AdjudicatorActionError(RuntimeError):
    pass


class BaseAdjudicatorActionView(LogActionMixin, SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    def get_action_log_fields(self, **kwargs):
        kwargs['adjudicator'] = self.adjudicator
        return super().get_action_log_fields(**kwargs)

    def get_redirect_url(self):
        return reverse_tournament('adjfeedback-overview', self.get_tournament())

    def get_adjudicator(self, request):
        try:
            adj_id = int(request.POST["adj_id"])
            adjudicator = Adjudicator.objects.get(id=adj_id)
        except (ValueError, Adjudicator.DoesNotExist, Adjudicator.MultipleObjectsReturned):
            raise AdjudicatorActionError("Whoops! I didn't recognise that adjudicator: {}".format(adj_id))
        return adjudicator

    def post(self, request, *args, **kwargs):
        try:
            self.adjudicator = self.get_adjudicator(request)
            self.modify_adjudicator(request, self.adjudicator)
            self.log_action()  # Need to call explicitly, since this isn't a form view
        except AdjudicatorActionError as e:
            messages.error(request, str(e))

        return super().post(request, *args, **kwargs)


class SetAdjudicatorTestScoreView(BaseAdjudicatorActionView):

    action_log_type = ActionLogEntry.ACTION_TYPE_TEST_SCORE_EDIT

    def get_action_log_fields(self, **kwargs):
        kwargs['adjudicator_test_score_history'] = self.atsh
        # Skip BaseAdjudicatorActionView
        return super(BaseAdjudicatorActionView, self).get_action_log_fields(**kwargs)

    def modify_adjudicator(self, request, adjudicator):
        try:
            score = float(request.POST["test_score"])
        except ValueError:
            raise AdjudicatorActionError("Whoops! The value \"{}\" isn't a valid test score.".format(score_text))

        adjudicator.test_score = score
        adjudicator.save()

        atsh = AdjudicatorTestScoreHistory(adjudicator=adjudicator,
                round=self.get_tournament().current_round, score=score)
        atsh.save()
        self.atsh = atsh


class SetAdjudicatorBreakingStatusView(BaseAdjudicatorActionView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATOR_BREAK_SET

    def modify_adjudicator(self, request, adjudicator):
        adjudicator.breaking = (str(request.POST["adj_breaking_status"]) == "true")
        adjudicator.save()

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)  # Discard redirect
        return HttpResponse("ok")


class SetAdjudicatorNoteView(BaseAdjudicatorActionView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATOR_NOTE_SET

    def modify_adjudicator(self, request, adjudicator):
        try:
            note = str(request.POST["note"])
        except ValueError as e:
            raise AdjudicatorActionError("Whoop! There was an error interpreting that string: " + str(e))

        adjudicator.notes = note
        adjudicator.save()


def get_feedback_progress(request, t):
    def calculate_coverage(submitted, total):
        if total == 0 or submitted == 0:
            return 0  # Avoid divide-by-zero error
        else:
            return int(submitted / total * 100)

    feedback = AdjudicatorFeedback.objects.select_related(
        'source_adjudicator__adjudicator', 'source_team__team').all()
    adjudicators = Adjudicator.objects.filter(tournament=t)
    adjudications = list(
        DebateAdjudicator.objects.select_related('adjudicator', 'debate').filter(
            debate__round__stage=Round.STAGE_PRELIMINARY))
    teams = Team.objects.filter(tournament=t)

    # Teams only owe feedback on non silent rounds
    rounds_owed = t.round_set.filter(
        silent=False, stage=Round.STAGE_PRELIMINARY, draw_status=t.current_round.STATUS_RELEASED).count()

    for adj in adjudicators:
        adj.total_ballots = 0
        adj.submitted_feedbacks = feedback.filter(source_adjudicator__adjudicator=adj)
        adjs_adjudications = [a for a in adjudications if a.adjudicator == adj]

        for item in adjs_adjudications:
            # Finding out the composition of their panel, tallying owed ballots
            if item.type == item.TYPE_CHAIR:
                adj.total_ballots += len(item.debate.adjudicators.trainees)
                adj.total_ballots += len(item.debate.adjudicators.panel)

            if item.type == item.TYPE_PANEL:
                # Panelists owe on chairs
                adj.total_ballots += 1

            if item.type == item.TYPE_TRAINEE:
                # Trainees owe on chairs
                adj.total_ballots += 1

        adj.submitted_ballots = max(adj.submitted_feedbacks.count(), 0)
        adj.owed_ballots = max((adj.total_ballots - adj.submitted_ballots), 0)
        adj.coverage = min(calculate_coverage(adj.submitted_ballots, adj.total_ballots), 100)

    for team in teams:
        team.submitted_ballots = max(feedback.filter(source_team__team=team).count(), 0)
        team.owed_ballots = max((rounds_owed - team.submitted_ballots), 0)
        team.coverage = min(calculate_coverage(team.submitted_ballots, rounds_owed), 100)

    return {'teams': teams, 'adjs': adjudicators}


@admin_required
@tournament_view
def feedback_progress(request, t):
    progress = get_feedback_progress(request, t)
    return render(request, 'feedback_progress.html',
                  dict(teams=progress['teams'], adjudicators=progress['adjs']))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('feedback_progress')
def public_feedback_progress(request, t):
    progress = get_feedback_progress(request, t)
    return render(request, 'public_feedback_progress.html',
                  dict(teams=progress['teams'], adjudicators=progress['adjs']))


class RandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, TemplateView):

    template_name = 'randomised_urls.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['teams'] = tournament.team_set.all()
        if not tournament.pref('share_adjs'):
            kwargs['adjs'] = tournament.adjudicator_set.all()
        else:
            kwargs['adjs'] = Adjudicator.objects.all()
        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()
        kwargs['tournament_slug'] = tournament.slug
        return super().get_context_data(**kwargs)


class GenerateRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    def get_redirect_url(self):
        return reverse_tournament('randomised-urls-view', self.get_tournament())

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()

        # Only works if there are no randomised URLs now
        if tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
                tournament.team_set.filter(url_key__isnull=False).exists():
            messages.error(self.request, "There are already randomised URLs. " +
                "You must use the Django management commands to populate or delete randomised URLs.")
        else:
            populate_url_keys(tournament.adjudicator_set.all())
            populate_url_keys(tournament.team_set.all())
            messages.success(self.request, "Randomised URLs were generated for all teams and adjudicators.")

        return super().post(request, *args, **kwargs)
