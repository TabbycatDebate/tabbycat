from actionlog.models import ActionLogEntry
from participants.models import Team
from tournaments.models import Round
from motions.models import Motion
from venues.models import Venue
from .models import TeamPositionAllocation, Debate, DebateTeam

from utils.views import *

import datetime

# Viewing Draw


@admin_required
@tournament_view
def draw_index(request, t):
    return r2r(request, 'draw_index.html')


@admin_required
@round_view
def draw_display_by_venue(request, round):
    draw = round.get_draw()
    return r2r(request,
               "draw_display_by_venue.html",
               dict(round=round,
                    draw=draw))


@admin_required
@round_view
def draw_display_by_team(request, round):
    draw = round.get_draw()
    return r2r(request, "draw_display_by_team.html", dict(draw=draw))

# Creating Draw


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
            return r2r(request,
                       "public_draw_released.html",
                       dict(draw=draw,
                            round=round))
        else:
            return r2r(request,
                       'public_draw_unreleased.html',
                       dict(draw=None,
                            round=round))

    raise


def assistant_draw(request, round):
    if round.draw_status == round.STATUS_RELEASED:
        return draw_confirmed(request, round)


def draw_none(request, round):
    all_teams_count = Team.objects.filter(tournament=round.tournament).count()
    active_teams = round.active_teams.all()
    active_venues_count = round.active_venues.count()
    active_adjs = round.active_adjudicators.count()
    rooms = float(active_teams.count()) // 2
    return r2r(request,
               "draw_none.html",
               dict(active_teams=active_teams,
                    active_venues_count=active_venues_count,
                    active_adjs=active_adjs,
                    rooms=rooms,
                    round=round,
                    all_teams_count=all_teams_count))


def draw_draft(request, round):
    draw = round.get_draw_with_standings(round)
    metrics = relevant_team_standings_metrics(round.tournament)
    return r2r(request, "draw_draft.html", dict(draw=draw, metrics=metrics))


def draw_confirmed(request, round):
    draw = round.get_cached_draw
    rooms = float(round.active_teams.count()) // 2
    active_adjs = round.active_adjudicators.all()

    return r2r(request,
               "draw_confirmed.html",
               dict(draw=draw,
                    active_adjs=active_adjs,
                    rooms=rooms))


@admin_required
@round_view
def draw_with_standings(request, round):
    draw = round.get_draw_with_standings(round)
    metrics = relevant_team_standings_metrics(round.tournament)
    return r2r(request,
               "draw_with_standings.html",
               dict(draw=draw,
                    metrics=metrics))


@admin_required
@expect_post
@round_view
def create_draw(request, round):
    round.draw()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_CREATE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)
    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def create_with_all(request, round):
    round.draw(override_team_checkins=True)
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_CREATE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)
    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def confirm_draw(request, round):

    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_CONFIRM,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def release_draw(request, round):
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw status is not CONFIRMED")

    round.draw_status = round.STATUS_RELEASED
    round.save()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_RELEASE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@expect_post
@round_view
def unrelease_draw(request, round):
    if round.draw_status != round.STATUS_RELEASED:
        return HttpResponseBadRequest("Draw status is not RELEASED")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_UNRELEASE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@tournament_view
def side_allocations(request, t):
    # TODO: move to draws app
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
        team.side_allocations = [tpas.get(
            (team.id, round.id), "-") for round in rounds]
    return r2r(request,
               "side_allocations.html",
               dict(teams=teams,
                    rounds=rounds))


@admin_required
@expect_post
@round_view
def set_round_start_time(request, round):

    time_text = request.POST["start_time"]
    try:
        time = datetime.datetime.strptime(time_text, "%H:%M").time()
    except ValueError as e:
        print(e)
        return redirect_round('draw', round)

    round.starts_at = time
    round.save()

    ActionLogEntry.objects.log(
        type=ActionLogEntry.ACTION_TYPE_ROUND_START_TIME_SET,
        user=request.user,
        round=round,
        tournament=round.tournament)

    return redirect_round('draw', round)


@admin_required
@round_view
def draw_matchups_edit(request, round):
    draw = round.get_draw_with_standings(round)
    debates = len(draw)
    unused_teams = round.unused_teams()
    possible_debates = len(unused_teams) // 2 + 1  # The blank rows to add
    possible_debates = [None] * possible_debates
    return r2r(request,
               "draw_matchups_edit.html",
               dict(draw=draw,
                    possible_debates=possible_debates,
                    unused_teams=unused_teams))


@admin_required
@expect_post
@round_view
def save_matchups(request, round):
    # TODO: move to draws app
    #print request.POST.keys()

    existing_debate_ids = [int(a.replace('debate_', ''))
                           for a in list(request.POST.keys())
                           if a.startswith('debate_')]
    for debate_id in existing_debate_ids:
        debate = Debate.objects.get(id=debate_id)
        new_aff_id = request.POST.get('aff_%s' % debate_id).replace('team_',
                                                                    '')
        new_neg_id = request.POST.get('neg_%s' % debate_id).replace('team_',
                                                                    '')

        if new_aff_id and new_neg_id:
            DebateTeam.objects.filter(debate=debate).delete()
            debate.save()

            new_aff_team = Team.objects.get(id=int(new_aff_id))
            new_aff_dt = DebateTeam(debate=debate,
                                    team=new_aff_team,
                                    position=DebateTeam.POSITION_AFFIRMATIVE)
            new_aff_dt.save()

            new_aff_team = Team.objects.get(id=int(new_neg_id))
            new_neg_dt = DebateTeam(debate=debate,
                                    team=new_aff_team,
                                    position=DebateTeam.POSITION_NEGATIVE)
            new_neg_dt.save()
        else:
            # If there's blank debates we need to delete those
            debate.delete()

    new_debate_ids = [int(a.replace('new_debate_', ''))
                      for a in list(request.POST.keys())
                      if a.startswith('new_debate_')]
    for debate_id in new_debate_ids:
        new_aff_id = request.POST.get('aff_%s' % debate_id).replace('team_',
                                                                    '')
        new_neg_id = request.POST.get('neg_%s' % debate_id).replace('team_',
                                                                    '')

        if new_aff_id and new_neg_id:
            debate = Debate(round=round, venue=None)
            debate.save()

            aff_team = Team.objects.get(id=int(new_aff_id))
            neg_team = Team.objects.get(id=int(new_neg_id))
            new_aff_dt = DebateTeam(debate=debate,
                                    team=aff_team,
                                    position=DebateTeam.POSITION_AFFIRMATIVE)
            new_neg_dt = DebateTeam(debate=debate,
                                    team=neg_team,
                                    position=DebateTeam.POSITION_NEGATIVE)
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
    # TODO: move to draws app
    def v_id(a):
        try:
            return int(request.POST[a].split('_')[1])
        except IndexError:
            return None

    data = [(int(a.split('_')[1]), v_id(a)) for a in list(request.POST.keys())]

    debates = Debate.objects.in_bulk([d_id for d_id, _ in data])
    venues = Venue.objects.in_bulk([v_id for _, v_id in data])
    for debate_id, venue_id in data:
        if venue_id == None:
            debates[debate_id].venue = None
        else:
            debates[debate_id].venue = venues[venue_id]

        debates[debate_id].save()

    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_VENUES_SAVE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)

    return HttpResponse("ok")

# Public


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_features__public_draw')
def public_draw(request, t):
    r = t.current_round
    if r.draw_status == r.STATUS_RELEASED:
        draw = r.get_draw()
        return r2r(request,
                   "public_draw_released.html",
                   dict(draw=draw,
                        round=r))
    else:
        return r2r(request,
                   'public_draw_unreleased.html',
                   dict(draw=None,
                        round=r))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_round_view('ui_options__show_all_draws')
def public_draw_by_round(request, round):
    if round.draw_status == round.STATUS_RELEASED:
        draw = round.get_draw()
        return r2r(request,
                   "public_draw_released.html",
                   dict(draw=draw,
                        round=round))
    else:
        return r2r(request,
                   'public_draw_unreleased.html',
                   dict(draw=None,
                        round=round))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def public_all_draws(request, t):
    all_rounds = list(Round.objects.filter(tournament=t))
    for r in all_rounds:
        r.draw = r.get_draw()

    return r2r(request,
               'public_draw_display_all.html',
               dict(all_rounds=all_rounds))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_features__public_side_allocations')
def public_side_allocations(request, t):
    # TODO: move to draws app
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
        team.side_allocations = [tpas.get(
            (team.id, round.id), "-") for round in rounds]
    return r2r(request,
               "public_side_allocations.html",
               dict(teams=teams,
                    rounds=rounds))

# Mastersheets


@login_required
@round_view
def master_sheets_list(request, round):
    venue_groups = VenueGroup.objects.all()
    return r2r(request,
               'master_sheets_list.html',
               dict(venue_groups=venue_groups))


@login_required
@round_view
def master_sheets_view(request, round, venue_group_id):
    # Temporary - pre unified venue groups
    base_venue_group = VenueGroup.objects.get(id=venue_group_id)
    active_tournaments = Tournament.objects.filter(active=True)

    for tournament in list(active_tournaments):
        tournament.debates = Debate.objects.select_related(
            'division', 'division__venue_group__short_name', 'round',
            'round__tournament', 'aff_team', 'neg_team').filter(
                # All Debates, with a matching round, at the same venue group name
                round__seq=round.seq,
                round__tournament=tournament,
                division__venue_group__short_name=
                base_venue_group.short_name  # hack - remove when venue groups are unified
            ).order_by('round', 'division__venue_group__short_name',
                       'division')

    return r2r(request,
               'master_sheets_view.html',
               dict(base_venue_group=base_venue_group,
                    active_tournaments=active_tournaments))


@admin_required
@round_view
def draw_print_feedback(request, round):
    draw = round.get_draw_by_room()
    config = round.tournament.config
    questions = round.tournament.adj_feedback_questions
    for question in questions:
        if question.choices:
            question.choice_options = question.choices.split("//")
        if question.min_value is not None and question.max_value is not None:
            step = max(
                (int(question.max_value) - int(question.min_value)) / 10, 1)
            question.number_options = list(range(
                int(question.min_value), int(question.max_value + 1), int(
                    step)))

    return r2r(request,
               "printing/feedback_list.html",
               dict(draw=draw,
                    config=config,
                    questions=questions))


@admin_required
@round_view
def draw_print_scoresheets(request, round):
    draw = round.get_draw_by_room()
    config = round.tournament.config
    motions = Motion.objects.filter(round=round)

    return r2r(request,
               "printing/scoresheet_list.html",
               dict(draw=draw,
                    config=config,
                    motions=motions))
