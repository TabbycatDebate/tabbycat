from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.conf import settings

from debate.models import Tournament, Round, Debate, Team, Venue, Adjudicator
from debate.models import AdjudicatorConflict, AdjudicatorInstitutionConflict, DebateAdjudicator, Speaker
from debate.models import Person, Checkin, Motion, ActionLog, BallotSubmission
from debate import forms

from django.forms.models import modelformset_factory
from django.forms import Textarea


from functools import wraps
import json

def redirect_round(to, round, **kwargs):
    return redirect(to, tournament_slug=round.tournament.slug,
                    round_seq=round.seq, *kwargs)

def redirect_tournament(to, tournament, **kwargs):
    return redirect(to, tournament_slug=tournament.slug, *kwargs)

def tournament_view(view_fn):
    @wraps(view_fn)
    def foo(request, tournament_slug, *args, **kwargs):
        return view_fn(request, request.tournament, *args, **kwargs)
    return foo

def round_view(view_fn):
    @wraps(view_fn)
    @tournament_view
    def foo(request, tournament, round_seq, *args, **kwargs):
        return view_fn(request, request.round, *args, **kwargs)
    return foo

def admin_required(view_fn):
    return user_passes_test(lambda u: u.is_superuser)(view_fn)


def expect_post(view_fn):
    @wraps(view_fn)
    def foo(request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        return view_fn(request, *args, **kwargs)
    return foo


def r2r(request, template, extra_context=None):
    rc = RequestContext(request)
    if extra_context:
        rc.update(extra_context)
    return render_to_response(template, context_instance=rc)


def index(request):
    tournaments = Tournament.objects.all()

    if request.user.is_authenticated():
        if len(tournaments) == 1:
            return redirect('tournament_home', tournament_slug=tournaments[0].slug)
        else:
            return r2r(request, 'index.html', dict(tournaments=Tournament.objects.all()))
    else:
        if len(tournaments) == 1:
            return redirect('public_index', tournament_slug=tournaments[0].slug)
        else:
            return r2r(request, 'index.html', dict(tournaments=Tournament.objects.all()))

## Public UI

@tournament_view
def public_index(request, t):
    return r2r(request, 'public/index.html')


@tournament_view
def public_participants(request, t):
    if request.tournament.config.get('public_participants') > 0:
        adjs = Adjudicator.objects.all()
        speakers = Speaker.objects.all()
        return r2r(request, "public/participants.html", dict(adjs=adjs, speakers=speakers))
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_draw(request, t):
    if request.tournament.config.get('public_draw') > 0:
        r = t.current_round
        if r.draw_status == r.STATUS_RELEASED:
            draw = r.get_draw()
            return r2r(request, "public/draw_released.html", dict(draw=draw, round=r))
        else:
            return r2r(request, 'public/draw_unreleased.html', dict(draw=None, round=r))
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_ballot_submit(request, t):
    if request.tournament.config.get('public_ballots') > 0:
        return r2r(request, 'public/add_ballot.html')
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_feedback_submit(request, t):
    if request.tournament.config.get('public_feedback') > 0:
        return r2r(request, 'public/add_feedback.html')
    else:
        return r2r(request, 'public/index.html')


@tournament_view
def public_feedback_progress(request, t):
    if request.tournament.config.get('feedback_progress') > 0:
        return r2r(request, 'public/feedback_tab.html')
    else:
        return r2r(request, 'public_index.html')

## Tab

@tournament_view
def public_team_tab(request, t):
    if request.tournament.config.get('tab_released') > 0:
        return r2r(request, 'public/team_tab.html')
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_speaker_tab(request, t):
    if request.tournament.config.get('tab_released') > 0:
        return r2r(request, 'public/speaker_tab.html')
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_replies_tab(request, t):
    if request.tournament.config.get('tab_released') > 0:
        return r2r(request, 'public/reply_tab.html')
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_motions_tab(request, t):
    if request.tournament.config.get('tab_released') > 0:
        return r2r(request, 'public/motions_tab.html')
    else:
        return r2r(request, 'public/index.html')

@tournament_view
def public_feedback_tab(request, t):
    if request.tournament.config.get('tab_released') > 0:
        return r2r(request, 'public/feedback_tab.html')
    else:
        return r2r(request, 'public_index.html')




@login_required
@tournament_view
def tournament_home(request, t):
    if not request.user.is_superuser:
        return redirect('results', tournament_slug=t.slug,
                        round_seq=t.current_round.seq)
    return r2r(request, 'tournament_home.html')

@login_required
def monkey_home(request, t):
    return r2r(request, 'monkey/home.html')


@admin_required
@tournament_view
def tournament_config(request, t):
    from debate.config import make_config_form

    context = {}
    if request.method == 'POST':
        form = make_config_form(t, request.POST)
        if form.is_valid():
            form.save()
            context['updated'] = True
    else:
        form = make_config_form(t)

    context['form'] = form

    return r2r(request, 'tournament_config.html', context)


@tournament_view
def feedback_progress(request, t):
    def calculate_coverage(submitted, total):
        if total == 0:
            return False # Don't show these ones
        elif submitted == 0:
            return 0
        else:
            return int((float(submitted) / float(total)) * 100)

    from debate.models import AdjudicatorFeedback
    feedback = AdjudicatorFeedback.objects.all()
    adjudicators = Adjudicator.objects.all()
    teams = Team.objects.all()
    current_round = request.tournament.current_round.seq

    for adj in adjudicators:
        adj.total_ballots = 0
        adj.submitted_feedbacks = feedback.filter(source_adjudicator__adjudicator = adj)
        adjudications = DebateAdjudicator.objects.filter(adjudicator = adj)

        for item in adjudications:
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
        team.owed_ballots = max((current_round - team.submitted_ballots), 0)
        team.coverage = min(calculate_coverage(team.submitted_ballots, current_round), 100)

    return r2r(request, 'wall_of_shame.html', dict(teams=teams, adjudicators=adjudicators))


@admin_required
@tournament_view
def draw_index(request, t):
    return r2r(request, 'draw_index.html')

@admin_required
@round_view
def round_index(request, round):
    return r2r(request, 'round_index.html')


@round_view
def checkin(request, round):
    context = {}
    if request.method == 'POST':
        v = request.POST.get('barcode_id')
        try:
            barcode_id = int(v)
            p = Person.objects.get(barcode_id=barcode_id)
            ch, created = Checkin.objects.get_or_create(
                person = p,
                round = round
            )
            context['person'] = p

        except (ValueError, Person.DoesNotExist):
            context['unknown_id'] = v

    return r2r(request, 'checkin.html', context)

@round_view
def post_checkin(request, round):
    v = request.POST.get('barcode_id')
    try:
        barcode_id = int(v)
        p = Person.objects.get(barcode_id=barcode_id)
        ch, created = Checkin.objects.get_or_create(
            person = p,
            round = round
        )

        message = p.checkin_message

        if not message:
            message = "Checked in %s" % p.name
        return HttpResponse(message)

    except (ValueError, Person.DoesNotExist):
        return HttpResponse("Unknown Id: %s" % v)

def _availability(request, round, model, context_name):

    items = getattr(round, '%s_availability' % model)()

    context = {
        context_name: items,
    }

    return r2r(request, '%s_availability.html' % model, context)


@admin_required
@round_view
def availability(request, round, model, context_name):
    return _availability(request, round, model, context_name)

@round_view
def checkin_results(request, round, model, context_name):
    return _availability(request, round, model, context_name)

def _update_availability(request, round, update_method, active_model, active_attr):

    if request.POST.get('copy'):
        prev_round = Round.objects.get(tournament=round.tournament,
                                       seq=round.seq-1)

        prev_objects = active_model.objects.filter(round=prev_round)
        available_ids = [getattr(o, '%s_id' % active_attr) for o in prev_objects]
        getattr(round, update_method)(available_ids)

        return HttpResponseRedirect(request.path.replace('update/', ''))

    available_ids = [int(a.replace("check_", "")) for a in request.POST.keys()
                     if a.startswith("check_")]

    getattr(round, update_method)(available_ids)

    return HttpResponse("ok")

@admin_required
@expect_post
@round_view
def update_availability(request, round, update_method, active_model, active_attr):
    return _update_availability(request, round, update_method, active_model, active_attr)

@expect_post
@round_view
def checkin_update(request, round, update_method, active_model, active_attr):
    return _update_availability(request, round, update_method, active_model, active_attr)


@admin_required
@round_view
def draw_display_by_venue(request, round):
    draw = round.get_draw()
    return r2r(request, "draw_display_by_venue.html", dict(round=round, draw=draw))

@admin_required
@round_view
def draw_display_by_team(request, round):
    draw = round.get_draw()
    return r2r(request, "draw_display_by_team.html", dict(draw=draw))

@round_view
def progress(request, round):
    draw = round.get_draw()

    stats = {
        'none': draw.filter(result_status=Debate.STATUS_NONE).count(),
        'draft': draw.filter(result_status=Debate.STATUS_DRAFT).count(),
        'confirmed': draw.filter(result_status=Debate.STATUS_CONFIRMED).count(),
    }
    stats['in'] = stats['confirmed']
    stats['out'] = stats['none'] + stats['draft']
    stats['pc'] = float(stats['in']) / (stats['out'] + stats['in']) * 100

    return r2r(request, "progress.html", stats)


@admin_required
@round_view
def draw(request, round):

    if round.draw_status == round.STATUS_NONE:
        return draw_none(request, round)

    if round.draw_status == round.STATUS_DRAFT:
        return draw_draft(request, round)

    if round.draw_status == round.STATUS_CONFIRMED:
        return draw_confirmed(request, round)

    if round.draw_status == round.STATUS_RELEASED:
        return draw_confirmed(request, round)

    raise


def draw_none(request, round):

    active_teams = round.active_teams.all()
    return r2r(request, "draw_none.html", dict(active_teams=active_teams))


def draw_draft(request, round):

    draw = round.get_draw()
    return r2r(request, "draw_draft.html", dict(draw=draw))


def draw_confirmed(request, round):

    draw = round.get_draw()
    return r2r(request, "draw_confirmed.html", dict(draw=draw))


@admin_required
@expect_post
@round_view
def create_draw(request, round):
    round.draw()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_CREATE,
        user=request.user, round=round)
    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def confirm_draw(request, round):

    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_CONFIRM,
        user=request.user, round=round)

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def create_adj_allocation(request, round):

    if round.draw_status != round.STATUS_CONFIRMED or round.STATUS_RELEASED:
        return HttpResponseBadRequest("Draw is not confirmed")

    from debate.adjudicator.hungarian import HungarianAllocator
    round.allocate_adjudicators(HungarianAllocator)

    return _json_adj_allocation(round.get_draw(), round.unused_adjudicators())


@admin_required
@expect_post
@round_view
def update_debate_importance(request, round):
    id = int(request.POST.get('debate_id'))
    im = int(request.POST.get('value'))
    debate = Debate.objects.get(pk=id)
    debate.importance = im
    debate.save()
    return HttpResponse(im)

@admin_required
@round_view
def motions(request, round):
    motions = [];

    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')

    for r in rounds:
        r_motions = Motion.objects.statistics(round=r)
        for m in r_motions:
            motions.append(m)

    return r2r(request, "motions.html", dict(motions=motions))

@admin_required
@round_view
def motions_edit(request, round):
    MotionFormSet = modelformset_factory(Motion,
        widgets={'text': Textarea()},
        can_delete=True, extra=3, exclude=['round'])

    if request.method == 'POST':
        formset = MotionFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for motion in formset.save(commit=False):
                motion.round = round
                motion.save()
                ActionLog.objects.log(type=ActionLog.ACTION_TYPE_MOTION_EDIT,
                    user=request.user, motion=motion)
            if 'submit' in request.POST:
                return redirect_round('motions', round)

    formset = MotionFormSet(queryset=Motion.objects.filter(round=round))

    return r2r(request, "motions_edit.html", dict(formset=formset))

@login_required
@round_view
def results(request, round):
    if not request.user.is_superuser:
        return monkey_results(request, round)

    draw = round.get_draw()

    stats = {
        'none': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=False).count(),
        'ballot_in': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=True).count(),
        'draft': draw.filter(result_status=Debate.STATUS_DRAFT).count(),
        'confirmed': draw.filter(result_status=Debate.STATUS_CONFIRMED).count(),
    }

    show_motions_column = Motion.objects.filter(round=round).count() > 1

    return r2r(request, "results.html", dict(draw=draw, stats=stats, show_motions_column=show_motions_column))

def monkey_results(request, round):

    if round != request.tournament.current_round:
        raise Http404()

    draw = round.get_draw()
    draw = draw.filter(result_status__in=(Debate.STATUS_NONE, Debate.STATUS_DRAFT))
    return r2r(request, "monkey/results.html", dict(draw=draw))


@login_required
@tournament_view
def edit_ballots(request, t, ballots_id):
    ballots = get_object_or_404(BallotSubmission, id=ballots_id)
    debate = ballots.debate

    if not request.user.is_superuser:
        template = 'monkey/enter_results.html'
        other_ballots_set = debate.ballotsubmission_set.exclude(id=ballots_id)
    else:
        template = 'enter_results.html'
        other_ballots_set = debate.ballotsubmission_set.exclude(id=ballots_id).exclude(discarded=True)

    if request.method == 'POST':
        form = forms.BallotSetForm(ballots, request.POST)

        if form.is_valid():
            form.save()

            # TODO add ballots to the ActionLog
            action_type = ActionLog.ACTION_TYPE_BY_RESULT_STATUS[debate.result_status]
            ActionLog.objects.log(type=action_type, user=request.user,
                debate=debate)

            return redirect_round('results', debate.round)
    else:
        form = forms.BallotSetForm(ballots)

    return r2r(request, template, dict(debate=debate, form=form,
        round=debate.round, ballots=ballots, other_ballots_set=other_ballots_set))

@login_required
@tournament_view
def new_ballots(request, t, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    ballots = BallotSubmission(
        debate         = debate,
        submitter_type = BallotSubmission.SUBMITTER_TABROOM,
        user           = request.user)

    if not request.user.is_superuser:
        template = 'monkey/enter_results.html'
    else:
        template = 'enter_results.html'

    if request.method == 'POST':
        form = forms.BallotSetForm(ballots, request.POST)

        if form.is_valid():
            form.save()

            # TODO add ballots to the ActionLog
            action_type = ActionLog.ACTION_TYPE_BY_RESULT_STATUS[debate.result_status]
            ActionLog.objects.log(type=action_type, user=request.user,
                debate=debate)

            return redirect_round('results', debate.round)

    else:
        form = forms.BallotSetForm(ballots)

    other_ballots_set = debate.ballotsubmission_set.all()

    return r2r(request, template, dict(debate=debate, form=form,
        round=debate.round, ballots=ballots, other_ballots_set=other_ballots_set,
        new=True))

@admin_required
@round_view
def team_standings(request, round):
    from debate.models import TeamScore
    teams = Team.objects.standings(round)

    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')

    def get_score(team, r):
        try:
            ts = TeamScore.objects.get(
                ballot_submission__confirmed=True,
                debate_team__team=team,
                debate_team__debate__round=r,
            )
            return ts.score, ts.points
        except TeamScore.DoesNotExist:
            return None

    for team in teams:
        setattr(team, 'results_in', get_score(team, round) is not None)
        team.scores = [get_score(team, r) for r in rounds]

    return r2r(request, 'team_standings.html', dict(teams=teams, rounds=rounds))
    # Comment out above line and uncomment below line to prevent access to team
    # standings.
    #return r2r(request, 'team_standings.html', dict(teams=None, rounds=rounds))

@admin_required
@round_view
def speaker_standings(request, round):
    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')
    speakers = Speaker.objects.standings(round.tournament, round)

    from debate.models import SpeakerScore
    def get_score(speaker, r):
        try:
            return SpeakerScore.objects.get(
                ballot_submission__confirmed=True,
                speaker=speaker,
                debate_team__debate__round=r,
                position__lte=3).score
        except SpeakerScore.DoesNotExist:
            return None

    for speaker in speakers:
        speaker.scores = [get_score(speaker, r) for r in rounds]
        speaker.results_in = get_score(speaker, round) is not None

    return r2r(request, 'speaker_standings.html', dict(speakers=speakers,
                                                       rounds=rounds))
    # Comment out above line and uncomment below line to prevent access to
    # speaker standings.
    #return r2r(request, 'speaker_standings.html', dict(speakers=None,
                                                       #rounds=rounds))

@admin_required
@round_view
def reply_standings(request, round):
    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')
    speakers = Speaker.objects.reply_standings(round.tournament, round)

    from debate.models import SpeakerScore
    def get_score(speaker, r):
        try:
            return SpeakerScore.objects.get(
                ballot_submission__confirmed=True,
                speaker=speaker,
                debate_team__debate__round=r,
                position=4).score
        except SpeakerScore.DoesNotExist:
            return None

    for speaker in speakers:
        speaker.scores = [get_score(speaker, r) for r in rounds]
        try:
            # TODO detect if the speaker's *team's* ballot has been entered
            # for this round, and set results_in accordingly.
            #SpeakerScore.objects.get(speaker=speaker,
                                     #debate_team__debate__round=r,
                                     #position=4)
            speaker.results_in = True
        except SpeakerScore.DoesNotExist:
            speaker.results_in = False

    return r2r(request, 'reply_standings.html', dict(speakers=speakers,
                                                       rounds=rounds))

@admin_required
@round_view
def draw_venues_edit(request, round):

    draw = round.get_draw()
    return r2r(request, "draw_venues_edit.html", dict(draw=draw))


@admin_required
@expect_post
@round_view
def save_venues(request, round):

    def v_id(a):
        try:
            return int(request.POST[a].split('_')[1])
        except IndexError:
            return None
    data = [(int(a.split('_')[1]), v_id(a))
             for a in request.POST.keys()]

    debates = Debate.objects.in_bulk([d_id for d_id, _ in data])
    venues = Venue.objects.in_bulk([v_id for _, v_id in data])
    for debate_id, venue_id in data:
        if venue_id == None:
            debates[debate_id].venue = None
        else:
            debates[debate_id].venue = venues[venue_id]

        debates[debate_id].save()

    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_VENUES_SAVE,
        user=request.user, round=round)

    return HttpResponse("ok")


@admin_required
@round_view
def draw_adjudicators_edit(request, round):

    draw = round.get_draw()
    return r2r(request, "draw_adjudicators_edit.html", dict(draw=draw))

def _json_adj_allocation(debates, unused_adj):

    obj = {}

    def _adj(a):
        return {
            'id': a.id,
            'name': a.name + " (" + a.institution.short_code + ")",
            'is_trainee': a.is_trainee,
        }

    def _debate(d):
        r = {}
        if d.adjudicators.chair:
            r['chair'] = _adj(d.adjudicators.chair)
        r['panel'] = [_adj(a) for a in d.adjudicators.panel]
        r['trainees'] = [_adj(a) for a in d.adjudicators.trainees]
        return r

    obj['debates'] = dict((d.id, _debate(d)) for d in debates)
    obj['unused'] = [_adj(a) for a in unused_adj]

    return HttpResponse(json.dumps(obj))


@admin_required
@round_view
def draw_adjudicators_get(request, round):

    draw = round.get_draw()

    return _json_adj_allocation(draw, round.unused_adjudicators())


@admin_required
@round_view
def save_adjudicators(request, round):
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    def id(s):
        s = s.replace('[]', '')
        return int(s.split('_')[1])

    debate_ids = set(id(a) for a in request.POST);
    debates = Debate.objects.in_bulk(list(debate_ids));
    debate_adjudicators = {}
    for d_id, debate in debates.items():
        a = debate.adjudicators
        a.delete()
        debate_adjudicators[d_id] = a

    for key, vals in request.POST.lists():
        if key.startswith("chair_"):
            debate_adjudicators[id(key)].chair = vals[0]
        if key.startswith("panel_"):
            for val in vals:
                debate_adjudicators[id(key)].panel.append(val)
        if key.startswith("trainees_"):
            for val in vals:
                debate_adjudicators[id(key)].trainees.append(val)

    # We don't do any validity checking here, so that the adjudication
    # core can save a work in progress.

    for d_id, alloc in debate_adjudicators.items():
        alloc.save()

    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_ADJUDICATORS_SAVE,
        user=request.user, round=round)

    return HttpResponse("ok")


@admin_required
@round_view
def adj_conflicts(request, round):

    data = {
        'conflict': {},
        'history': {},
    }

    def add(type, adj_id, target_id):
        if adj_id not in data[type]:
            data[type][adj_id] = []
        data[type][adj_id].append(target_id)

    for ac in AdjudicatorConflict.objects.all():
        add('conflict', ac.adjudicator_id, ac.team_id)

    for ic in AdjudicatorInstitutionConflict.objects.all():
        for team in Team.objects.filter(institution=ic.institution):
            add('conflict', ic.adjudicator_id, team.id)

    history = DebateAdjudicator.objects.filter(
        debate__round__seq__lt = round.seq,
    )

    for da in history:
        add('history', da.adjudicator_id, da.debate.aff_team.id)
        add('history', da.adjudicator_id, da.debate.neg_team.id)

    return HttpResponse(json.dumps(data), mimetype="text/json")


@admin_required
@tournament_view
def adj_scores(request, t):
    data = {}

    #TODO: make round-dependent
    for adj in Adjudicator.objects.all():
        data[adj.id] = adj.score

    return HttpResponse(json.dumps(data), mimetype="text/json")


@login_required
@tournament_view
def adj_feedback(request, t):
    if not request.user.is_superuser:
        template = 'monkey/adjudicator_feedback.html'
    else:
        template = 'adjudicator_feedback.html'

    adjudicators = Adjudicator.objects.all()
    return r2r(request, template, dict(adjudicators=adjudicators))


@login_required
@tournament_view
def get_adj_feedback(request, t):

    adj = get_object_or_404(Adjudicator, pk=int(request.GET['id']))
    feedback = adj.get_feedback()
    data = [ [unicode(f.round),
              f.debate.bracket,
              unicode(f.debate),
              unicode(f.source),
              f.score,
              f.comments,
             ] for f in feedback ]

    return HttpResponse(json.dumps({'aaData': data}), mimetype="text/json")


@login_required
@tournament_view
def enter_feedback(request, t, adjudicator_id):

    adj = get_object_or_404(Adjudicator, id=adjudicator_id)

    if not request.user.is_superuser:
        template = 'monkey/enter_feedback.html'
    else:
        template = 'enter_feedback.html'

    if request.method == "POST":
        form = forms.make_feedback_form_class(adj)(request.POST)
        if form.is_valid():
            adj_feedback = form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_FEEDBACK_SAVE,
                user=request.user, adjudicator_feedback=adj_feedback)
            return redirect_tournament('adj_feedback', t)
    else:
        form = forms.make_feedback_form_class(adj)()

    return r2r(request, template, dict(adj=adj, form=form))

@admin_required
@round_view
def ballot_checkin(request, round):
    ballots_left = ballot_checkin_number_left(round)
    return r2r(request, 'ballot_checkin.html', dict(ballots_left=ballots_left))

class DebateBallotCheckinError(Exception):
    pass

def get_debate_from_ballot_checkin_request(request, round):
    # Called by the submit button on the ballot checkin form.
    # Returns the message that should go in the "success" field.
    v = request.POST.get('venue')

    try:
        venue = Venue.objects.get(name__iexact=v)
    except Venue.DoesNotExist:
        raise DebateBallotCheckinError('There aren\'t any venues with the name "' + v + '".')

    try:
        debate = Debate.objects.get(round=round, venue=venue)
    except Debate.DoesNotExist:
        raise DebateBallotCheckinError('There wasn\'t a debate in venue ' + venue.name + ' this round.')

    if debate.ballot_in:
        raise DebateBallotCheckinError('The ballot for venue ' + venue.name + ' has already been checked in.')

    return debate

def ballot_checkin_number_left(round):
    count = Debate.objects.filter(round=round, ballot_in=False).count()
    return count

@admin_required
@round_view
def ballot_checkin_get_details(request, round):
    try:
        debate = get_debate_from_ballot_checkin_request(request, round)
    except DebateBallotCheckinError, e:
        data = {'exists': False, 'message': str(e)}
        return HttpResponse(json.dumps(data))

    obj = dict()

    obj['exists'] = True
    obj['venue'] = debate.venue.name
    obj['aff_team'] = debate.aff_team.short_name
    obj['neg_team'] = debate.neg_team.short_name

    adjs = debate.adjudicators
    adj_names = [adj.name for type, adj in adjs if type != DebateAdjudicator.TYPE_TRAINEE]
    obj['num_adjs'] = len(adj_names)
    obj['adjudicators'] = adj_names

    obj['ballots_left'] = ballot_checkin_number_left(round)

    return HttpResponse(json.dumps(obj))

@admin_required
@round_view
def post_ballot_checkin(request, round):
    try:
        debate = get_debate_from_ballot_checkin_request(request, round)
    except DebateBallotCheckinError, e:
        data = {'exists': False, 'message': str(e)}
        return HttpResponse(json.dumps(data))

    debate.ballot_in = True
    debate.save()

    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_BALLOT_CHECKIN,
        user=request.user, debate=debate)

    obj = dict()

    obj['success'] = True
    obj['venue'] = debate.venue.name
    obj['debate_description'] = debate.aff_team.name + " vs " + debate.neg_team.name

    obj['ballots_left'] = ballot_checkin_number_left(round)

    return HttpResponse(json.dumps(obj))
