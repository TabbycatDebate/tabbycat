from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.conf import settings
from django.views.decorators.cache import cache_page
from ipware.ip import get_real_ip

from debate.result import BallotSet
from debate import forms
from debate.models import *
from debate.utils import populate_url_keys

from venues.models import VenueGroup, Venue

from motions.models import Motion
from action_log.models import ActionLog

from django.forms.models import modelformset_factory, formset_factory
from django.forms import Textarea

import datetime
from functools import wraps
import json

def get_ip_address(request):
    ip = get_real_ip(request)
    if ip is None:
        return "0.0.0.0"
    return ip

def decide_show_draw_strength(tournament):
    return tournament.config.get('team_standings_rule') == "nz"

def redirect_round(to, round, **kwargs):
    return redirect(to, tournament_slug=round.tournament.slug,
                    round_seq=round.seq, *kwargs)

def redirect_tournament(to, tournament, **kwargs):
    return redirect(to, tournament_slug=tournament.slug, **kwargs)

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

def public_optional_tournament_view(config_option):
    def bar(view_fn):
        @wraps(view_fn)
        @tournament_view
        def foo(request, tournament, *args      , **kwargs):
            if tournament.config.get(config_option):
                return view_fn(request, tournament, *args, **kwargs)
            else:
                return redirect_tournament('public_index', tournament)
        return foo
    return bar

def public_optional_round_view(config_option):
    def bar(view_fn):
        @wraps(view_fn)
        @round_view
        def foo(request, round, *args, **kwargs):
            if round.tournament.config.get(config_option):
                return view_fn(request, round, *args, **kwargs)
            else:
                return redirect_tournament('public_index', round.tournament)
        return foo
    return bar

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
@public_optional_tournament_view('public_draw')
def public_draw(request, t):
    r = t.current_round
    if r.draw_status == r.STATUS_RELEASED:
        draw = r.get_draw()
        return r2r(request, "public/public_draw_released.html", dict(draw=draw, round=r))
    else:
        return r2r(request, 'public/public_draw_unreleased.html', dict(draw=None, round=r))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_round_view('show_all_draws')
def public_draw_by_round(request, round):
    if round.draw_status == round.STATUS_RELEASED:
        draw = round.get_draw()
        return r2r(request, "public/public_draw_released.html", dict(draw=draw, round=round))
    else:
        return r2r(request, 'public/public_draw_unreleased.html', dict(draw=None, round=round))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_team_standings')
def public_team_standings(request, t):
    print "Generating public team standings"
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

        from debate.models import TeamScore

        # Ranking by institution__name and reference isn't the same as ordering by
        # short_name, which is what we really want. But we can't rank by short_name,
        # because it's not a field (it's a property). So we'll do this in JavaScript.
        # The real purpose of this ordering is to obscure the *true* ranking of teams
        # - teams are not supposed to know rankings between teams on the same number
        # of wins.
        teams = Team.objects.order_by('institution__code', 'reference')
        rounds = t.prelim_rounds(until=round).filter(silent=False).order_by('seq')

        def get_round_result(team, r):
            try:
                ts = TeamScore.objects.get(
                    ballot_submission__confirmed=True,
                    debate_team__team=team,
                    debate_team__debate__round=r,
                )
                ts.opposition = ts.debate_team.opposition.team
                return ts
            except TeamScore.DoesNotExist:
                return None

        for team in teams:
            team.round_results = [get_round_result(team, r) for r in rounds]
            # Do this manually, in case there are silent rounds
            team.wins = [ts.win for ts in team.round_results if ts].count(True)
            team.points = sum([ts.points for ts in team.round_results if ts])


        return r2r(request, 'public/public_team_standings.html', dict(teams=teams, rounds=rounds, round=round))
    else:
        return r2r(request, 'public/index.html')


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_ballots')
def public_ballot_submit(request, t):
    r = t.current_round

    das = DebateAdjudicator.objects.filter(debate__round=r).select_related('adjudicator', 'debate')

    if r.draw_status == r.STATUS_RELEASED and r.motions_good_for_public:
        draw = r.get_draw()
        return r2r(request, 'public/public_add_ballot.html', dict(das=das))
    else:
        return r2r(request, 'public/public_add_ballot_unreleased.html', dict(das=None, round=r))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_motions')
def public_motions(request, t):
    order_by = t.config.get('public_motions_descending') and '-seq' or 'seq'
    rounds = Round.objects.filter(motions_released=True, tournament=t).order_by(order_by)
    return r2r(request, 'public/public_motions.html', dict(rounds=rounds))

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


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def public_all_draws(request, t):
    all_rounds = list(Round.objects.filter(tournament=t))
    for r in all_rounds:
        r.draw = r.get_draw()

    return r2r(request, 'public/public_draw_display_all.html', dict(
        all_rounds=all_rounds))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_side_allocations')
def public_side_allocations(request, t):
    teams = Team.objects.filter(tournament=t)
    rounds = Round.objects.filter(tournament=t).order_by("seq")
    tpas = dict()
    TPA_MAP = {
        TeamPositionAllocation.POSITION_AFFIRMATIVE: "Aff",
        TeamPositionAllocation.POSITION_NEGATIVE: "Neg",
    }
    for tpa in TeamPositionAllocation.objects.all():
        tpas[(tpa.team.id, tpa.round.seq)] = TPA_MAP[tpa.position]
    for team in teams:
        team.side_allocations = [tpas.get((team.id, round.id), "-") for round in rounds]
    return r2r(request, "public/public_side_allocations.html", dict(teams=teams, rounds=rounds))

## Tab


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('ballots_released')
def public_ballots_view(request, t, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    if debate.result_status != Debate.STATUS_CONFIRMED:
        raise Http404()

    round = debate.round
    # Can't see results for current round or later
    if (round.seq > round.tournament.current_round.seq and not round.tournament.release_all) or round.silent:
        raise Http404()

    ballot_submission = debate.confirmed_ballot
    if ballot_submission is None:
        raise Http404()

    ballot_set = BallotSet(ballot_submission)
    return r2r(request, 'public/public_ballot_set.html', dict(debate=debate, ballot_set=ballot_set))

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

@login_required
@tournament_view
def results_status_update(request, t):

    # Draw Status
    draw = t.current_round.get_draw()

    stats_none = draw.filter(result_status=Debate.STATUS_NONE).count()
    stats_draft = draw.filter(result_status=Debate.STATUS_DRAFT).count()
    stats_confirmed = draw.filter(result_status=Debate.STATUS_CONFIRMED).count()

    total = stats_none + stats_draft + stats_confirmed

    stats = [[0,stats_confirmed], [0,stats_draft], [0,stats_none]]

    return HttpResponse(json.dumps(stats), content_type="text/json")



@admin_required
@tournament_view
def draw_index(request, t):
    return r2r(request, 'draw_index.html')

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
@round_view
def draw_display_by_venue(request, round):
    draw = round.get_draw()
    return r2r(request, "draw_display_by_venue.html", dict(round=round, draw=draw))

@admin_required
@round_view
def draw_display_by_team(request, round):
    draw = round.get_draw()
    return r2r(request, "draw_display_by_team.html", dict(draw=draw))

@login_required
@round_view
def draw(request, round):

    if request.user.is_superuser:
        if round.draw_status == round.STATUS_NONE:
            return draw_none(request, round)

        if round.draw_status == round.STATUS_DRAFT:
            return draw_draft(request, round)

        if round.draw_status == round.STATUS_CONFIRMED:
            return draw_confirmed(request, round)

        if round.draw_status == round.STATUS_RELEASED:
            return draw_confirmed(request, round)
    else:
        if round.draw_status == round.STATUS_RELEASED:
            draw = round.get_draw()
            return r2r(request, "public/public_draw_released.html", dict(draw=draw, round=round))
        else:
            return r2r(request, 'public/public_draw_unreleased.html', dict(draw=None, round=round))

    raise

def assistant_draw(request, round):
    if round.draw_status == round.STATUS_RELEASED:
        return draw_confirmed(request, round)


def draw_none(request, round):
    all_teams_count = Team.objects.filter(tournament=round.tournament).count()
    active_teams = round.active_teams.all()
    active_venues_count = round.active_venues.count()
    active_adjs = round.active_adjudicators.count()
    rooms = float(active_teams.count()) / 2
    return r2r(request, "draw_none.html", dict(active_teams=active_teams,
                                               active_venues_count=active_venues_count,
                                               active_adjs=active_adjs,
                                               rooms=rooms,
                                               round=round,
                                               all_teams_count=all_teams_count))


def draw_draft(request, round):
    draw = round.get_draw_with_standings(round)
    show_draw_strength = decide_show_draw_strength(round.tournament)
    return r2r(request, "draw_draft.html", dict(draw=draw, show_draw_strength=show_draw_strength))


def draw_confirmed(request, round):
    draw = round.get_cached_draw
    rooms = float(round.active_teams.count()) / 2
    active_adjs = round.active_adjudicators.all()

    return r2r(request, "draw_confirmed.html", dict(draw=draw,
                                                    active_adjs=active_adjs,
                                                    rooms=rooms))








@admin_required
@round_view
def draw_with_standings(request, round):
    draw = round.get_draw_with_standings(round)
    show_draw_strength = decide_show_draw_strength(round.tournament)
    return r2r(request, "draw_with_standings.html", dict(draw=draw, show_draw_strength=show_draw_strength))

@admin_required
@expect_post
@round_view
def create_draw(request, round):
    round.draw()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_CREATE,
        user=request.user, round=round, tournament=round.tournament)
    return redirect_round('draw', round)

@admin_required
@expect_post
@round_view
def create_draw_with_all_teams(request, round):
    round.draw(override_team_checkins=True)
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_CREATE,
        user=request.user, round=round, tournament=round.tournament)
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
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def release_draw(request, round):
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw status is not CONFIRMED")

    round.draw_status = round.STATUS_RELEASED
    round.save()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_RELEASE,
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def unrelease_draw(request, round):
    if round.draw_status != round.STATUS_RELEASED:
        return HttpResponseBadRequest("Draw status is not RELEASED")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DRAW_UNRELEASE,
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@tournament_view
def side_allocations(request, t):
    teams = Team.objects.filter(tournament=t)
    rounds = Round.objects.filter(tournament=t).order_by("seq")
    tpas = dict()
    TPA_MAP = {
        TeamPositionAllocation.POSITION_AFFIRMATIVE: "Aff",
        TeamPositionAllocation.POSITION_NEGATIVE: "Neg",
        None: "-"
    }
    for tpa in TeamPositionAllocation.objects.all():
        tpas[(tpa.team.id, tpa.round.seq)] = TPA_MAP[tpa.position]
    for team in teams:
        team.side_allocations = [tpas.get((team.id, round.id), "-") for round in rounds]
    return r2r(request, "side_allocations.html", dict(teams=teams, rounds=rounds))


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
@expect_post
@round_view
def set_round_start_time(request, round):

    time_text = request.POST["start_time"]
    try:
        time = datetime.datetime.strptime(time_text, "%H:%M").time()
    except ValueError, e:
        print e
        return redirect_round('draw', round)

    round.starts_at = time
    round.save()

    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_ROUND_START_TIME_SET,
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('draw', round)


@login_required
@round_view
def results(request, round):

    draw = round.get_draw()
    stats = {
        'none': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=False).count(),
        'ballot_in': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=True).count(),
        'draft': draw.filter(result_status=Debate.STATUS_DRAFT).count(),
        'confirmed': draw.filter(result_status=Debate.STATUS_CONFIRMED).count(),
        'postponed': draw.filter(result_status=Debate.STATUS_POSTPONED).count(),
    }

    if not request.user.is_superuser:
        if round != request.tournament.current_round:
            raise Http404()
        template = "assistant/assistant_results.html"
        draw = draw.filter(result_status__in=(
            Debate.STATUS_NONE, Debate.STATUS_DRAFT, Debate.STATUS_POSTPONED))
    else:
        template = "results.html"

    num_motions = Motion.objects.filter(round=round).count()
    show_motions_column = num_motions > 1
    has_motions = num_motions > 0

    return r2r(request, template, dict(draw=draw, stats=stats,
        show_motions_column=show_motions_column, has_motions=has_motions)
    )

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_round_view('public_results')
def public_results(request, round):
    # Can't see results for current round or later
    if (round.seq >= round.tournament.current_round.seq and not round.tournament.release_all) or round.silent:
        print "Result page denied: round %d, current round %d, release all %s, silent %s" % (round.seq, round.tournament.current_round.seq, round.tournament.release_all, round.silent)
        raise Http404()
    draw = round.get_draw()
    show_motions_column = Motion.objects.filter(round=round).count() > 1 and round.tournament.config.get('show_motions_in_results')
    show_splits = round.tournament.config.get('show_splitting_adjudicators')
    show_ballots = round.tournament.config.get('ballots_released')
    return r2r(request, "public/public_results_for_round.html", dict(
            draw=draw, show_motions_column=show_motions_column, show_splits=show_splits,
            show_ballots=show_ballots))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_results')
def public_results_index(request, tournament):
    rounds = Round.objects.filter(tournament=tournament,
        seq__lt=tournament.current_round.seq, silent=False).order_by('seq')
    return r2r(request, "public/public_results_index.html", dict(rounds=rounds))

@login_required
@tournament_view
def edit_ballotset(request, t, ballotsub_id):
    ballotsub = get_object_or_404(BallotSubmission, id=ballotsub_id)
    debate = ballotsub.debate

    if not request.user.is_superuser:
        all_ballotsubs = debate.ballotsubmission_set_by_version_except_discarded
    else:
        all_ballotsubs = debate.ballotsubmission_set_by_version

    identical_ballotsubs_dict = debate.identical_ballotsubs_dict
    for b in all_ballotsubs:
        if b in identical_ballotsubs_dict:
            b.identical_ballotsub_versions = identical_ballotsubs_dict[b]

    if request.method == 'POST':
        form = forms.BallotSetForm(ballotsub, request.POST)

        if form.is_valid():
            form.save()

            if ballotsub.discarded:
                action_type = ActionLog.ACTION_TYPE_BALLOT_DISCARD
                messages.success(request, "Ballot set for %s discarded." % debate.matchup)
            elif ballotsub.confirmed:
                ballotsub.confirmer = request.user
                ballotsub.confirm_timestamp = datetime.datetime.now()
                ballotsub.save()
                action_type = ActionLog.ACTION_TYPE_BALLOT_CONFIRM
                messages.success(request, "Ballot set for %s confirmed." % debate.matchup)
            else:
                action_type = ActionLog.ACTION_TYPE_BALLOT_EDIT
                messages.success(request, "Edits to ballot set for %s saved." % debate.matchup)
            ActionLog.objects.log(type=action_type, user=request.user,
                ballot_submission=ballotsub, ip_address=get_ip_address(request), tournament=t)

            return redirect_round('results', debate.round)
    else:
        form = forms.BallotSetForm(ballotsub)

    template = 'enter_results.html' if request.user.is_superuser else 'assistant/assistant_enter_results.html'
    context = {
        'form'             : form,
        'ballotsub'        : ballotsub,
        'debate'           : debate,
        'all_ballotsubs'   : all_ballotsubs,
        'disable_confirm'  : request.user == ballotsub.submitter and not t.config.get('enable_assistant_confirms') and not request.user.is_superuser,
        'round'            : debate.round,
        'not_singleton'    : all_ballotsubs.exclude(id=ballotsub_id).exists(),
        'new'              : False,
        'show_adj_contact' : True,
    }
    return r2r(request, template, context)

# Don't cache
@public_optional_tournament_view('public_ballots_randomised')
def public_new_ballotset_key(request, t, url_key):
    adjudicator = get_object_or_404(Adjudicator, tournament=t, url_key=url_key)
    return public_new_ballotset(request, t, adjudicator)

# Don't cache
@public_optional_tournament_view('public_ballots')
def public_new_ballotset_id(request, t, adj_id):
    adjudicator = get_object_or_404(Adjudicator, tournament=t, id=adj_id)
    return public_new_ballotset(request, t, adjudicator)

def public_new_ballotset(request, t, adjudicator):
    round = t.current_round

    if round.draw_status != Round.STATUS_RELEASED or not round.motions_released:
        return r2r(request, 'public/public_enter_results_error.html', dict(adjudicator=adjudicator,
                message='The draw and/or motions for the round haven\'t been released yet.'))
    try:
        da = DebateAdjudicator.objects.get(adjudicator=adjudicator, debate__round=round)
    except DebateAdjudicator.DoesNotExist:
        return r2r(request, 'public/public_enter_results_error.html', dict(adjudicator=adjudicator,
                message='It looks like you don\'t have a debate this round.'))

    ip_address = get_ip_address(request)
    ballotsub = BallotSubmission(debate=da.debate, ip_address=ip_address,
            submitter_type=BallotSubmission.SUBMITTER_PUBLIC)

    if request.method == 'POST':
        form = forms.BallotSetForm(ballotsub, request.POST, password=True)
        if form.is_valid():
            form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_BALLOT_SUBMIT,
                    ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            return r2r(request, 'public/public_success.html', dict(success_kind="ballot"))
    else:
        form = forms.BallotSetForm(ballotsub, password=True)

    context = {
        'form'                : form,
        'debate'              : da.debate,
        'round'               : round,
        'ballotsub'           : ballotsub,
        'adjudicator'         : adjudicator,
        'existing_ballotsubs' : da.debate.ballotsubmission_set.exclude(discarded=True).count(),
        'show_adj_contact'    : False,
    }
    return r2r(request, 'public/public_enter_results.html', context)

@login_required
@tournament_view
def new_ballotset(request, t, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    ip_address = get_ip_address(request)
    ballotsub = BallotSubmission(debate=debate, submitter=request.user,
            submitter_type=BallotSubmission.SUBMITTER_TABROOM, ip_address=ip_address)

    if not debate.adjudicators.has_chair:
        return HttpResponseBadRequest("Whoops! This debate doesn't have a chair, so you can't enter results for it.")

    if request.method == 'POST':
        form = forms.BallotSetForm(ballotsub, request.POST)
        if form.is_valid():
            form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_BALLOT_CREATE, user=request.user,
                    ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            messages.success(request, "Ballot set for %s added." % debate.matchup)
            return redirect_round('results', debate.round)
    else:
        form = forms.BallotSetForm(ballotsub)

    template = 'enter_results.html' if request.user.is_superuser else 'assistant/assistant_enter_results.html'
    all_ballotsubs = debate.ballotsubmission_set_by_version if request.user.is_superuser \
            else debate.ballotsubmission_set_by_version_except_discarded
    context = {
        'form'             : form,
        'ballotsub'        : ballotsub,
        'debate'           : debate,
        'round'            : debate.round,
        'all_ballotsubs'   : all_ballotsubs,
        'not_singleton'    : all_ballotsubs.exists(),
        'new'              : True,
        'show_adj_contact' : True,
    }
    return r2r(request, template, context)


@login_required
@tournament_view
@expect_post
def toggle_postponed(request, t):
    debate_id = request.POST.get('debate')
    debate = Debate.objects.get(pk=debate_id)
    if debate.result_status == debate.STATUS_POSTPONED:
        debate.result_status = debate.STATUS_NONE
    else:
        debate.result_status = debate.STATUS_POSTPONED

    print debate.result_status
    debate.save()
    return HttpResponse("ok")



@admin_required
@round_view
def draw_matchups_edit(request, round):
    draw = round.get_draw_with_standings(round)
    debates = len(draw)
    unused_teams = round.unused_teams()
    possible_debates = int(len(unused_teams) / 2) + 1 # The blank rows to add
    possible_debates = [None] * possible_debates
    return r2r(request, "draw_matchups_edit.html", dict(draw=draw,
        possible_debates=possible_debates,unused_teams=unused_teams))

@admin_required
@expect_post
@round_view
def save_matchups(request, round):
    #print request.POST.keys()

    existing_debate_ids = [int(a.replace('debate_', '')) for a in request.POST.keys() if a.startswith('debate_')]
    for debate_id in existing_debate_ids:
        debate = Debate.objects.get(id=debate_id)
        new_aff_id = request.POST.get('aff_%s' % debate_id).replace('team_', '')
        new_neg_id = request.POST.get('neg_%s' % debate_id).replace('team_', '')

        if new_aff_id and new_neg_id:
            DebateTeam.objects.filter(debate=debate).delete()
            debate.save()

            new_aff_team = Team.objects.get(id=int(new_aff_id))
            new_aff_dt = DebateTeam(debate=debate, team=new_aff_team, position=DebateTeam.POSITION_AFFIRMATIVE)
            new_aff_dt.save()

            new_aff_team = Team.objects.get(id=int(new_neg_id))
            new_neg_dt = DebateTeam(debate=debate, team=new_aff_team, position=DebateTeam.POSITION_NEGATIVE)
            new_neg_dt.save()
        else:
            # If there's blank debates we need to delete those
            debate.delete()

    new_debate_ids = [int(a.replace('new_debate_', '')) for a in request.POST.keys() if a.startswith('new_debate_')]
    for debate_id in new_debate_ids:
        new_aff_id = request.POST.get('aff_%s' % debate_id).replace('team_', '')
        new_neg_id = request.POST.get('neg_%s' % debate_id).replace('team_', '')

        if new_aff_id and new_neg_id:
            debate = Debate(round=round, venue=None)
            debate.save()

            aff_team = Team.objects.get(id=int(new_aff_id))
            neg_team = Team.objects.get(id=int(new_neg_id))
            new_aff_dt = DebateTeam(debate=debate, team=aff_team, position=DebateTeam.POSITION_AFFIRMATIVE)
            new_neg_dt = DebateTeam(debate=debate, team=neg_team, position=DebateTeam.POSITION_NEGATIVE)
            new_aff_dt.save()
            new_neg_dt.save()

    return HttpResponse("ok")

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
        user=request.user, round=round, tournament=round.tournament)

    return HttpResponse("ok")


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


@login_required
@round_view
def master_sheets_list(request, round):
    venue_groups = VenueGroup.objects.all()
    return r2r(request, 'master_sheets_list.html', dict(venue_groups=venue_groups))


@login_required
@round_view
def master_sheets_view(request, round, venue_group_id):
    # Temporary - pre unified venue groups
    base_venue_group = VenueGroup.objects.get(id=venue_group_id)
    active_tournaments = Tournament.objects.filter(active=True)

    for tournament in list(active_tournaments):
        tournament.debates = Debate.objects.select_related(
            'division','division__venue_group__short_name','round','round__tournament','aff_team','neg_team'
        ).filter(
            # All Debates, with a matching round, at the same venue group name
            round__seq=round.seq,
            round__tournament=tournament,
            division__venue_group__short_name=base_venue_group.short_name # hack - remove when venue groups are unified
        ).order_by('round','division__venue_group__short_name','division')

    return r2r(request, 'master_sheets_view.html', dict(
        base_venue_group=base_venue_group,
        active_tournaments=active_tournaments
    ))


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
            user=request.user, debate=debate, tournament=round.tournament)

    obj = dict()

    obj['success'] = True
    obj['venue'] = debate.venue.name
    obj['debate_description'] = debate.aff_team.short_name + " vs " + debate.neg_team.short_name

    obj['ballots_left'] = ballot_checkin_number_left(round)

    return HttpResponse(json.dumps(obj))

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
