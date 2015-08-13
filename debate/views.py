from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

from results.result import BallotSet
from debate.keys import populate_url_keys

from debate.models import *
from venues.models import VenueGroup, Venue
from motions.models import Motion
from draws.models import Debate
from action_log.models import ActionLog

from debate import forms
from django.forms.models import modelformset_factory, formset_factory
from django.forms import Textarea

import json

from utils import *

def index(request):
    tournaments = Tournament.objects.all()
    if request.user.is_authenticated():
        return r2r(request, 'site_index.html', dict(tournaments=Tournament.objects.all()))
    elif len(tournaments) == 1:
        sole_tournament = list(tournaments)[0]
        return redirect_tournament('public_index', sole_tournament)
    else:
        return r2r(request, 'site_index.html', dict(tournaments=Tournament.objects.all()))

## Public UI

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@tournament_view
def team_speakers(request, t, team_id):
    from django.http import JsonResponse
    team = Team.objects.get(pk=team_id)
    speakers = team.speakers
    data = {}
    for i, speaker in enumerate(speakers):
        data[i] = speaker.name

    return JsonResponse(data, safe=False)


@cache_page(10) # Set slower to show new indexes so it will show new pages
@tournament_view
def public_index(request, t):
    return r2r(request, 'public/public_tournament_index.html')


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_participants')
def public_participants(request, t):
    adjs = Adjudicator.objects.all()
    speakers = Speaker.objects.all().select_related('team','team__institution')
    return r2r(request, "public/public_participants.html", dict(adjs=adjs, speakers=speakers))



@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = set(d.venue_group for d in divisions)
    for uvg in venue_groups:
        uvg.divisions = [d for d in divisions if d.venue_group == uvg]

    return r2r(request, 'public/public_divisions.html', dict(venue_groups=venue_groups))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_venues(request, t):
    venues = VenueGroup.objects.all()
    return r2r(request, 'public/public_all_tournament_venues.html', dict(venues=venues))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_draws_for_venue(request, t, venue_id):
    venue_group = VenueGroup.objects.get(pk=venue_id)
    debates = Debate.objects.filter(division__venue_group=venue_group).select_related(
        'round','round__tournament','division')
    return r2r(request, 'public/public_all_draws_for_venue.html', dict(
        venue_group=venue_group, debates=debates))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_institutions(request, t):
    institutions = Institution.objects.all()
    return r2r(request, 'public/public_all_tournament_institutions.html', dict(
        institutions=institutions))

@tournament_view
def all_draws_for_institution(request, t, institution_id):
    # TODO: move to draws app
    institution = Institution.objects.get(pk=institution_id)
    debate_teams = DebateTeam.objects.filter(team__institution=institution).select_related(
        'debate', 'debate__division', 'debate__division__venue_group', 'debate__round')
    debates = [dt.debate for dt in debate_teams]

    return r2r(request, 'public/public_all_draws_for_institution.html', dict(
        institution=institution, debates=debates))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_teams(request, t):
    teams = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
    return r2r(request, 'public/public_all_tournament_teams.html', dict(
        teams=teams))



## Tab

@login_required
@tournament_view
def tournament_home(request, t):
    round = t.current_round
    # This should never happen, but if it does, fail semi-gracefully
    if round is None:
        if request.user.is_superuser:
            return HttpResponseBadRequest("You need to set the current round. <a href=\"/admin/debate/tournament\">Go to Django admin.</a>")
        else:
            raise Http404()

    rounds = t.prelim_rounds(until=round).order_by('seq')

    # Draw Status
    draw = round.get_draw()
    total_ballots = draw.count()
    stats_none = draw.filter(result_status=Debate.STATUS_NONE).count()
    stats_draft = draw.filter(result_status=Debate.STATUS_DRAFT).count()
    stats_confirmed = draw.filter(result_status=Debate.STATUS_CONFIRMED).count()
    stats = [[0,stats_confirmed], [0,stats_draft], [0,stats_none]]

    return r2r(request, 'tournament_home.html', dict(stats=stats,
        total_ballots=total_ballots, round=round))



@admin_required
@round_view
def round_index(request, round):
    return r2r(request, 'round_index.html')

@admin_required
@round_view
def round_increment_check(request, round):
    if round != request.tournament.current_round: # doesn't make sense if not current round
        raise Http404()
    num_unconfirmed = round.get_draw().filter(result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    increment_ok = num_unconfirmed == 0
    return r2r(request, "round_increment_check.html", dict(num_unconfirmed=num_unconfirmed, increment_ok=increment_ok))

@admin_required
@expect_post
@round_view
def round_increment(request, round):
    if round != request.tournament.current_round: # doesn't make sense if not current round
        raise Http404()
    request.tournament.advance_round()
    return redirect_round('draw', request.tournament.current_round )


# public (for barcode checkins)
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








@admin_required
@tournament_view
def division_allocations(request, t):
    teams = Team.objects.filter(tournament=t).all()
    divisions = Division.objects.filter(tournament=t).all()
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = VenueGroup.objects.all()

    return r2r(request, "division_allocations.html", dict(teams=teams, divisions=divisions, venue_groups=venue_groups))


@admin_required
@expect_post
@tournament_view
def save_divisions(request, t):
    culled_dict = dict((int(k), int(v)) for k, v in request.POST.iteritems() if v)

    teams = Team.objects.in_bulk([t_id for t_id in culled_dict.keys()])
    divisions = Division.objects.in_bulk([d_id for d_id in culled_dict.values()])

    for team_id, division_id in culled_dict.iteritems():
        teams[team_id].division = divisions[division_id]
        teams[team_id].save()

    # ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DIVISIONS_SAVE,
    #     user=request.user, tournament=t)

    return HttpResponse("ok")

@admin_required
@expect_post
@tournament_view
def create_division_allocation(request, t):
    from debate.division_allocator import DivisionAllocator

    teams = list(Team.objects.filter(tournament=t))
    for team in teams:
        preferences = list(TeamVenuePreference.objects.filter(team=team))
        team.preferences_dict = dict((p.priority, p.venue_group) for p in preferences)

    # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
    divisions = Division.objects.filter(tournament=t).delete()

    venue_groups = VenueGroup.objects.all()

    alloc = DivisionAllocator(teams=teams, divisions=divisions,venue_groups=venue_groups, tournament=t)
    success = alloc.allocate()

    if success:
        return HttpResponse("ok")
    else:
        return HttpResponseBadRequest("Couldn't create divisions")

@admin_required
@expect_post
@round_view
def create_adj_allocation(request, round):

    if round.draw_status == round.STATUS_RELEASED:
        return HttpResponseBadRequest("Draw is already released, unrelease draw to redo auto-allocation.")
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw is not confirmed, confirm draw to run auto-allocation.")

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
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT,
            user=request.user, debate=debate, tournament=round.tournament)
    return HttpResponse(im)


@admin_required
@round_view
def draw_adjudicators_edit(request, round):
    context = dict()
    context['draw'] = draw = round.get_draw()
    context['adj0'] = Adjudicator.objects.first()
    context['duplicate_adjs'] = round.tournament.config.get('duplicate_adjs')
    context['feedback_headings'] = [q.name for q in round.tournament.adj_feedback_questions]

    def calculate_prior_adj_genders(team):
        debates = team.get_debates(round.seq)
        adjs = DebateAdjudicator.objects.filter(debate__in=debates).count()
        male_adjs = DebateAdjudicator.objects.filter(debate__in=debates,adjudicator__gender="M").count()
        if male_adjs > 0:
            male_adj_percent = int((float(male_adjs) / float(adjs)) * 100)
            return male_adj_percent
        else:
            return 0

    for debate in draw:
        aff_male_adj_percent = calculate_prior_adj_genders(debate.aff_team)
        debate.aff_team.male_adj_percent = aff_male_adj_percent

        neg_male_adj_percent = calculate_prior_adj_genders(debate.neg_team)
        debate.neg_team.male_adj_percent = neg_male_adj_percent

        if neg_male_adj_percent > aff_male_adj_percent:
            debate.gender_class = (neg_male_adj_percent / 5) - 10
        else:
            debate.gender_class = (aff_male_adj_percent / 5) - 10

    regions = round.tournament.region_set.order_by('name')
    break_categories = round.tournament.breakcategory_set.order_by('seq').exclude(is_general=True)
    colors = ["#C70062", "#00C79B", "#B1E001", "#476C5E", "#777", "#FF2983", "#6A268C", "#00C0CF", "#0051CF"]
    context['regions'] = zip(regions, colors + ["black"] * (len(regions) - len(colors)))
    context['break_categories'] = zip(break_categories, colors + ["black"] * (len(break_categories) - len(colors)))

    return r2r(request, "draw_adjudicators_edit.html", context)

def _json_adj_allocation(debates, unused_adj):

    obj = {}

    def _adj(a):

        if a.institution.region:
            region_name = "region-%s" % a.institution.region.id
        else:
            region_name = ""

        return {
            'id': a.id,
            'name': a.name + " (" + a.institution.short_code + ")",
            'is_unaccredited': a.is_unaccredited,
            'gender': a.gender,
            'region': region_name
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
        user=request.user, round=round, tournament=round.tournament)

    return HttpResponse("ok")


@admin_required
@round_view
def adj_conflicts(request, round):

    data = {
        'personal': {},
        'history': {},
        'institutional': {},
        'adjudicator': {},
    }

    def add(type, adj_id, target_id):
        if adj_id not in data[type]:
            data[type][adj_id] = []
        data[type][adj_id].append(target_id)

    for ac in AdjudicatorConflict.objects.all():
        add('personal', ac.adjudicator_id, ac.team_id)

    for ic in AdjudicatorInstitutionConflict.objects.all():
        for team in Team.objects.filter(institution=ic.institution):
            add('institutional', ic.adjudicator_id, team.id)

    for ac in AdjudicatorAdjudicatorConflict.objects.all():
        add('adjudicator', ac.adjudicator_id, ac.conflict_adjudicator.id)

    history = DebateAdjudicator.objects.filter(
        debate__round__seq__lt = round.seq,
    )

    for da in history:
        add('history', da.adjudicator_id, da.debate.aff_team.id)
        add('history', da.adjudicator_id, da.debate.neg_team.id)

    return HttpResponse(json.dumps(data), content_type="text/json")



@admin_required
@tournament_view
def randomised_urls(request, t):
    context = dict()
    context['teams'] = t.team_set.all()
    context['adjs'] = t.adjudicator_set.all()
    context['exists'] = t.adjudicator_set.filter(url_key__isnull=False).exists() or \
            t.team_set.filter(url_key__isnull=False).exists()
    context['tournament_slug'] = t.slug
    context['ballot_normal_urls_enabled'] = t.config.get('public_ballots')
    context['ballot_randomised_urls_enabled'] = t.config.get('public_ballots_randomised')
    context['feedback_normal_urls_enabled'] = t.config.get('public_feedback')
    context['feedback_randomised_urls_enabled'] = t.config.get('public_feedback_randomised')
    return r2r(request, 'randomised_urls.html', context)

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