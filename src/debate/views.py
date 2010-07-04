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
from debate.models import AdjudicatorConflict, DebateAdjudicator, Speaker
from debate.models import Person, Checkin
from debate import forms

from debate import wordpresslib

from functools import wraps
import json

def get_wordpress_client():
    return wordpresslib.WordPressClient(
        settings.WORDPRESS_URL,
        settings.WORDPRESS_USER,
        settings.WORDPRESS_PASSWORD,
    )

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


@login_required
def index(request):
    tournaments = Tournament.objects.all()
    if len(tournaments) == 1:
        return redirect('tournament_home', tournament_slug=tournaments[0].slug)
    return r2r(request, 'index.html',
               dict(tournaments=Tournament.objects.all()))


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

    items = getattr(round, '%s_availability' % model)().order_by('name')
    
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
@expect_post
@round_view
def wordpress_post_draw(request, round):

    client = get_wordpress_client()

    post = wordpresslib.WordPressPost()
    post.title = 'Draw for Round %d' % round.seq
    draw = round.get_unordered_draw()
    post.description = str(render_to_string('wp_draw.html', {'round': round,
                                                             'draw': draw}))

    post.categories = (settings.WORDPRESS_DRAW_CATEGORY_ID,)

    post_id = client.newPost(post, False)

    return redirect_round('draw', round)

@admin_required
@expect_post
@round_view
def wordpress_post_standings(request, round):
    from debate.models import TeamScore

    teams = Team.objects.standings(round).order_by('-points', 'name')

    client = get_wordpress_client()

    post = wordpresslib.WordPressPost()
    post.title = 'Standings after Round %d' % round.seq
    post.description = str(render_to_string('wp_standings.html', {'teams':
                                                                  teams},))

    post.categories = (settings.WORDPRESS_DRAW_CATEGORY_ID,)

    post_id = client.newPost(post, False)

    return redirect_round('draw', round)


@admin_required
@round_view
def draw_display(request, round):
    draw = round.get_draw().order_by('venue__name')
    return r2r(request, "draw_display.html", dict(draw=draw))


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
    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def confirm_draw(request, round):

    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def create_adj_allocation(request, round):

    if round.draw_status != round.STATUS_CONFIRMED:
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


@login_required
@round_view
def results(request, round):
    if not request.user.is_superuser:
        return monkey_results(request, round)

    draw = round.get_draw()

    stats = {
        'none': draw.filter(result_status=Debate.STATUS_NONE).count(),
        'draft': draw.filter(result_status=Debate.STATUS_DRAFT).count(),
        'confirmed': draw.filter(result_status=Debate.STATUS_CONFIRMED).count(),
    }
    return r2r(request, "results.html", dict(draw=draw, stats=stats))

def monkey_results(request, round):

    if round != request.tournament.current_round:
        raise Http404()

    draw = round.get_draw()
    draw = draw.filter(result_status__in=(Debate.STATUS_NONE,
                                           Debate.STATUS_DRAFT))
    return r2r(request, "monkey/results.html", dict(draw=draw))


@login_required
@tournament_view
def enter_result(request, t, debate_id): 
    debate = get_object_or_404(Debate, id=debate_id)

    if not request.user.is_superuser:
        template = 'monkey/enter_results.html'
    else:
        template = 'enter_results.html'

    if request.method == 'POST':
        form = forms.ResultForm(debate, request.POST)

        if form.is_valid():
            form.save()
            return redirect_round('results', debate.round)
    else:
        form = forms.ResultForm(debate)

    return r2r(request, template, dict(debate=debate, form=form,
                                                   round=debate.round))


@admin_required
@round_view
def team_standings(request, round):
    from debate.models import TeamScore
    teams = Team.objects.standings(round)

    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')

    def get_score(team, r):
        try:
            return TeamScore.objects.get(
                debate_team__team=team,
                debate_team__debate__round=r,
            ).score
        except TeamScore.DoesNotExist:
            return None

    for team in teams:
        setattr(team, 'results_in', team.results_count >= round.seq)
        team.scores = [get_score(team, r) for r in rounds]

    return r2r(request, 'team_standings.html', dict(teams=teams, rounds=rounds))

@admin_required
@round_view
def speaker_standings(request, round):
    rounds = Round.objects.filter(tournament=round.tournament,
                                  seq__lte=round.seq).order_by('seq')
    speakers = Speaker.objects.standings(round.tournament, round)

    from debate.models import SpeakerScore
    def get_score(speaker, r):
        try:
            return SpeakerScore.objects.get(speaker=speaker,
                                    debate_team__debate__round=r,
                                    position__lte=3).score
        except SpeakerScore.DoesNotExist:
            return None

    for speaker in speakers:
        speaker.scores = [get_score(speaker, r) for r in rounds]
        try:
            SpeakerScore.objects.get(speaker=speaker,
                                     debate_team__debate__round=r,
                                     position__lte=3)
            speaker.results_in = True
        except SpeakerScore.DoesNotExist:
            speaker.results_in = False

    return r2r(request, 'speaker_standings.html', dict(speakers=speakers,
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
            'name': a.name,
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

    for d_id, alloc in debate_adjudicators.items():
        alloc.save()

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
            form.save()
            return redirect_tournament('adj_feedback', t)
    else:
        form = forms.make_feedback_form_class(adj)()
    
    return r2r(request, template, dict(adj=adj, form=form))

