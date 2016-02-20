import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
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
from utils.misc import reverse_tournament
from utils.mixins import SingleObjectByRandomisedUrlMixin, PublicCacheMixin
from utils.urlkeys import populate_url_keys
from utils.views import *

from .models import AdjudicatorFeedback, AdjudicatorTestScoreHistory
from .forms import make_feedback_form_class

@admin_required
@tournament_view
def adj_scores(request, t):
    data = {}

    #TODO: make round-dependent
    for adj in Adjudicator.objects.all().select_related('tournament','tournament__current_round'):
        data[adj.id] = adj.score

    return HttpResponse(json.dumps(data), content_type="text/json")

@admin_required
@tournament_view
def feedback_overview(request, t):
    breaking_count = 0

    if not t.pref('share_adjs'):
        adjudicators = Adjudicator.objects.filter(tournament=t).select_related(
            'tournament','tournament__current_round')
    else:
        adjudicators = Adjudicator.objects.all()

    all_debate_adjudicators = list(DebateAdjudicator.objects.select_related('adjudicator').all())
    all_adj_scores = list(SpeakerScoreByAdj.objects.select_related('debate_adjudicator','ballot_submission').filter(
        ballot_submission__confirmed=True))

    # Processing scores to get average margins
    for adj in adjudicators:
        adj_debateadjudications  = [a for a in all_debate_adjudicators if a.adjudicator is adj]
        adj_scores = [s for s in all_adj_scores if s.debate_adjudicator is adj_debateadjudications]

        adj.debates = len(adj_debateadjudications)
        if adj.breaking:
            breaking_count += 1

        if len(adj_scores) > 0:
            adj.avg_score = sum(s.score for s in adj_scores) / len(adj_scores)

            ballot_ids = []
            ballot_margins = []
            for score in adj_scores:
                ballot_ids.append(score.ballot_submission)

            ballot_ids = sorted(set([b.id for b in ballot_ids])) # Deduplication of ballot IDS

            for ballot_id in ballot_ids:
                # For each unique ballot id, total its scores
                single_round = adj_scores.filter(ballot_submission=ballot_id)
                scores = [s.score for s in single_round] # TODO this is slow - should be prefetched
                slice_end = len(scores)
                teamA = sum(scores[:len(scores)/2])
                teamB = sum(scores[len(scores)/2:])
                ballot_margins.append(max(teamA, teamB) - min(teamA, teamB))

            adj.avg_margin = sum(ballot_margins) / len(ballot_margins)

        else:
            adj.avg_score = None
            adj.avg_margin = None

    all_adj_feedbacks = list(AdjudicatorFeedback.objects.filter(
            confirmed=True).exclude(source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE).select_related(
        'adjudicator', 'source_adjudicator__debate__round', 'source_team__debate__round'))
    rounds = t.prelim_rounds(until=t.current_round)

    # Filtering/summing feedback by round for the graphs (faster than a model method)
    for adj in adjudicators:
        adj.rscores = []
        adj_feedbacks = [f for f in all_adj_feedbacks if f.adjudicator == adj]
        for r in rounds:
            adj_round_feedbacks = [f for f in adj_feedbacks if (f.source_adjudicator and f.source_adjudicator.debate.round == r)]
            adj_round_feedbacks.extend([f for f in adj_feedbacks if (f.source_team and f.source_team.debate.round == r)])

            if len(adj_round_feedbacks) > 0:
                # Getting the position of the adj
                # We grab both so there is at least one valid debate, then lookup the debate adjudicator for that
                debates = [fb.source_team.debate for fb in adj_round_feedbacks if fb.source_team]
                debates.extend([fb.source_adjudicator.debate for fb in adj_round_feedbacks if fb.source_adjudicator])
                adj_da = next((da for da in all_debate_adjudicators if (da.adjudicator == adj and da.debate == debates[0])), None)
                if adj_da:
                    if adj_da.type == adj_da.TYPE_CHAIR:
                        adj_type = "Chair"
                    elif adj_da.type == adj_da.TYPE_PANEL:
                        adj_type = "Panellist"
                    elif adj_da.type == adj_da.TYPE_TRAINEE:
                        adj_type = "Trainee"

                    # Average their scores for that round
                    totals = [f.score for f in adj_round_feedbacks]
                    average = sum(totals) / len(totals)

                    # Creating the object list for the graph
                    adj.rscores.append([r.seq, average, adj_type])
                else:
                    print('none')

    context = {
        'adjudicators'      : adjudicators,
        'breaking_count'    : breaking_count,
        'feedback_headings' : [q.name for q in t.adj_feedback_questions],
        'score_min'         : t.pref('adj_min_score'),
        'score_max'         : t.pref('adj_max_score'),
    }
    return render(request, 'feedback_overview.html', context)


@login_required
@tournament_view
def adj_source_feedback(request, t):
    questions = t.adj_feedback_questions

    teams_data = []
    teams = Team.objects.filter(tournament=t)
    for team in teams:
        feedbacks = AdjudicatorFeedback.objects.filter(source_team__team=team).select_related(
            'source_team__team').count()
        teams_data.append({
            'name': team.short_name,
            'institution': team.institution.name,
            'feedbacks': "%s Feedbacks" % feedbacks,
            'rowLink': reverse('team_feedback_list', args=[t.slug, team.id]),
        })

    adjs_data = []
    adjs = Adjudicator.objects.filter(tournament=t).order_by('name')
    for adj in adjs:
        feedbacks = AdjudicatorFeedback.objects.filter(source_adjudicator__adjudicator=adj).select_related(
        'source_adjudicator__adjudicator').count(),
        adjs_data.append({
            'name': adj.name,
            'institution': adj.institution.name,
            'feedbacks': "%s Feedbacks" % feedbacks,
            'rowLink': reverse('adj_feedback_list', args=[t.slug, adj.id]),
        })

    return render(request, "adjudicator_source_list.html", dict(teams=json.dumps(teams_data), adjs=json.dumps(adjs_data)))

def process_feedback(feedbacks, t):
    questions = t.adj_feedback_questions
    score_step = t.pref('adj_max_score') / 10
    score_thresholds = {
        'low_score'     : t.pref('adj_min_score') + score_step,
        'medium_score'  : t.pref('adj_min_score') + score_step + score_step,
        'high_score'    : t.pref('adj_max_score') - score_step,
    }
    for feedback in feedbacks:
        feedback.items = []
        for question in questions:
            try:
                qa_set = { "question" : question,
                           "answer"   : question.answer_set.get(feedback=feedback).answer}
                feedback.items.append(qa_set)
            except ObjectDoesNotExist:
                pass
    return feedbacks, score_thresholds

@login_required
@tournament_view
def adj_latest_feedback(request, t):
    feedbacks = AdjudicatorFeedback.objects.order_by('-timestamp')[:50].select_related(
        'adjudicator', 'source_adjudicator__adjudicator', 'source_team__team')
    feedbacks, score_thresholds = process_feedback(feedbacks, t)
    if feedbacks.count() == 0:
        messages.info(request, "No feedback has been submitted yet.")
    return render(request, "feedback_latest.html", dict(feedbacks=feedbacks,  score_thresholds=score_thresholds))

@login_required
@tournament_view
def team_feedback_list(request, t, team_id):
    team = Team.objects.get(pk=team_id)
    source = team.short_name
    feedbacks = AdjudicatorFeedback.objects.filter(source_team__team=team).order_by('-timestamp')
    feedbacks, score_thresholds = process_feedback(feedbacks, t)
    return render(request, "feedback_by_source.html", dict(source_name=source, feedbacks=feedbacks, score_thresholds=score_thresholds))

@login_required
@tournament_view
def adj_feedback_list(request, t, adj_id):
    adj = Adjudicator.objects.get(pk=adj_id)
    source = adj.name
    feedbacks = AdjudicatorFeedback.objects.filter(source_adjudicator__adjudicator=adj).order_by('-timestamp')
    feedbacks, score_thresholds = process_feedback(feedbacks, t)
    return render(request, "feedback_by_source.html", dict(source_name=source, feedbacks=feedbacks, score_thresholds=score_thresholds))

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


class PublicFeedbackSuccessView(TemplateView):
    template_name = "public_success.html"

    def get_context_data(self, **kwargs):
        kwargs['success_kind'] = "feedback"
        return super().get_context_data(**kwargs)


class BaseAddFeedbackView(LogActionMixin, SingleObjectMixin, FormView):
    """Base class for views that allow users to add feedback.
    Subclasses must also subclass SingleObjectMixin, directly or indirectly."""

    template_name = "enter_feedback.html"
    pk_url_kwarg = 'source_id'

    def get_form_class(self):
        return make_feedback_form_class(self.object, self.get_submitter_fields(),
                **self.feedback_form_class_kwargs)

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
            kwargs['source_name'] = source.name
        elif isinstance(source, Team):
            kwargs['source_type'] = "team"
            kwargs['source_name'] = source.short_name
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class TabroomAddFeedbackView(TabroomSubmissionFieldsMixin, TournamentMixin, LoginRequiredMixin, BaseAddFeedbackView):
    """View for tabroom officials to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SAVE
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': False,
        'include_unreleased_draws': True,
    }

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, "Feedback from %s on %s added." % (
                self.adj_feedback.source, self.adj_feedback.adjudicator))
        return result

    def get_success_url(self):
        return reverse_tournament('add_feedback', self.get_tournament())


class PublicAddFeedbackView(PublicSubmissionFieldsMixin, PublicTournamentPageMixin, BaseAddFeedbackView):
    """Base class for views for public users to add feedback."""

    action_log_type = ActionLogEntry.ACTION_TYPE_FEEDBACK_SUBMIT
    feedback_form_class_kwargs = {
        'confirm_on_submit': True,
        'enforce_required': True,
        'include_unreleased_draws': False,
    }

    def get_success_url(self):
        return reverse_tournament('adjfeedback-public-success', self.get_tournament())


class PublicAddFeedbackByRandomisedUrlView(SingleObjectByRandomisedUrlMixin, PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is a randomised one."""
    public_page_preference = 'public_feedback_randomised'


class PublicAddFeedbackByIdUrlView(PublicAddFeedbackView):
    """View for public users to add feedback, where the URL is by object ID."""
    public_page_preference = 'public_feedback'


class PublicAddFeedbackIndexView(PublicCacheMixin, PublicTournamentPageMixin, TemplateView):
    """View for the index page for public users to add feedback. The index page
    lists all possible sources; public users should then choose themselves."""

    template_name = "public_add_feedback.html"
    public_page_preference = 'public_feedback'

    def get_context_data(self, **kwargs):
        kwargs['adjudicators'] = Adjudicator.objects.all()
        kwargs['teams'] = Team.objects.all()
        return super().get_context_data(**kwargs)


@admin_required
@expect_post
@tournament_view
def set_adj_test_score(request, t):

    try:
        adj_id = int(request.POST["adj_test_id"])
    except ValueError:
        return HttpResponseBadRequest("Score value is not legit")

    try:
        adjudicator = Adjudicator.objects.get(id=adj_id)
    except (Adjudicator.DoesNotExist, Adjudicator.MultipleObjectsReturned):
        return HttpResponseBadRequest("Adjudicator probably doesn't exist")

    # CONTINUE HERE CONTINUE HERE WORK IN PROGRESS
    score_text = request.POST["test_score"]
    try:
        score = float(score_text)
    except ValueError as e:
        print(e)
        return redirect_tournament('feedback_overview', t)

    adjudicator.test_score = score
    adjudicator.save()

    atsh = AdjudicatorTestScoreHistory(adjudicator=adjudicator,
        round=t.current_round, score=score)
    atsh.save()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_TEST_SCORE_EDIT,
        user=request.user, adjudicator_test_score_history=atsh, tournament=t)

    return redirect_tournament('feedback_overview', t)


# TODO: move to breaking app?
@admin_required
@expect_post
@tournament_view
def set_adj_breaking_status(request, t):
    adj_id = int(request.POST["adj_id"])
    adj_breaking_status = str(request.POST["adj_breaking_status"])

    try:
        adjudicator = Adjudicator.objects.get(id=adj_id)
    except (Adjudicator.DoesNotExist, Adjudicator.MultipleObjectsReturned):
        return HttpResponseBadRequest("Adjudicator probably doesn't exist")

    if adj_breaking_status == "true":
        adjudicator.breaking = True
    else:
        adjudicator.breaking = False

    adjudicator.save()
    return HttpResponse("ok")

@login_required
@tournament_view
def add_feedback(request, t):
    context = {
        'adjudicators' : t.adjudicator_set.all() if not t.pref('share_adjs')
                         else Adjudicator.objects.all(),
        'teams'        : t.team_set.all(),
    }
    if request.user.is_superuser:
        template = 'add_feedback.html'
    else:
        template = 'assistant_add_feedback.html'
    return render(request, template, context)


def get_feedback_progress(request, t):
    def calculate_coverage(submitted, total):
        if total == 0 or submitted == 0:
            return 0 # avoid divide-by-zero error
        else:
            return int(submitted / total * 100)

    feedback = AdjudicatorFeedback.objects.select_related('source_adjudicator__adjudicator','source_team__team').all()
    adjudicators = Adjudicator.objects.filter(tournament=t)
    adjudications = list(DebateAdjudicator.objects.select_related('adjudicator','debate').all())
    teams = Team.objects.filter(tournament=t)

    # Teams only owe feedback on non silent rounds
    rounds_owed = t.round_set.filter(silent=False,  draw_status=t.current_round.STATUS_RELEASED).count()

    for adj in adjudicators:
        adj.total_ballots = 0
        adj.submitted_feedbacks = feedback.filter(source_adjudicator__adjudicator = adj)
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
        team.submitted_ballots = max(feedback.filter(source_team__team = team).count(), 0)
        team.owed_ballots = max((rounds_owed - team.submitted_ballots), 0)
        team.coverage = min(calculate_coverage(team.submitted_ballots, rounds_owed), 100)

    return { 'teams': teams, 'adjs': adjudicators }


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


# TODO: move to a different app?
@admin_required
@expect_post
@tournament_view
def set_adj_note(request, t):
    try:
        adj_id = str(request.POST["adj_test_id"])
    except ValueError:
        return HttpResponseBadRequest("Note value is not legit")

    try:
        adjudicator = Adjudicator.objects.get(id=adj_id)
    except (Adjudicator.DoesNotExist, Adjudicator.MultipleObjectsReturned):
        return HttpResponseBadRequest("Adjudicator probably doesn't exist")

    # CONTINUE HERE CONTINUE HERE WORK IN PROGRESS
    note_text = request.POST["note"]
    try:
        note = str(note_text)
    except ValueError as e:
        print(e)
        return redirect_tournament('feedback_overview', t)

    adjudicator.notes = note
    adjudicator.save()

    return redirect_tournament('feedback_overview', t)


@admin_required
@tournament_view
def randomised_urls(request, t):
    context = dict()
    context['teams'] = t.team_set.all()
    context['adjs'] = t.adjudicator_set.all()
    context['exists'] = t.adjudicator_set.filter(url_key__isnull=False).exists() or \
            t.team_set.filter(url_key__isnull=False).exists()
    context['tournament_slug'] = t.slug
    context['ballot_normal_urls_enabled'] = t.pref('public_ballots')
    context['ballot_randomised_urls_enabled'] = t.pref('public_ballots_randomised')
    context['feedback_normal_urls_enabled'] = t.pref('public_feedback')
    context['feedback_randomised_urls_enabled'] = t.pref('public_feedback_randomised')
    return render(request, 'randomised_urls.html', context)

@admin_required
@tournament_view
@expect_post
def generate_randomised_urls(request, t):
    # Only works if there are no randomised URLs now
    if t.adjudicator_set.filter(url_key__isnull=False).exists() or \
            t.team_set.filter(url_key__isnull=False).exists():
        return HttpResponseBadRequest("There are already randomised URLs. You must use the Django management commands to populate or delete randomised URLs.")

    populate_url_keys(t.adjudicator_set.all())
    populate_url_keys(t.team_set.all())
    return redirect_tournament('randomised_urls', t)
