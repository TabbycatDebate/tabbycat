from tournaments.models import Round
from participants.models import Person
from actionlog.models import ActionLogEntry
from .models import ActiveVenue, ActiveTeam, ActiveAdjudicator

from utils.views import *


@admin_required
@round_view
def availability_index(request, round):
    from draw.models import Debate
    if round.prev:
        previous_unconfirmed = round.prev.get_draw().filter(
            result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    else:
        previous_unconfirmed = None

    t = round.tournament
    checks = [{
        'type'      : "Team",
        'total'     : t.teams.count(),
        'in_now'    : ActiveTeam.objects.filter(round=round).count(),
        'in_before' : ActiveTeam.objects.filter(round=round.prev).count() if round.prev else None,
    }, {
        'type'      : "Adjudicator",
        'total'     : round.tournament.adjudicator_set.count(),
        'in_now'    : ActiveAdjudicator.objects.filter(round=round).count(),
        'in_before' : ActiveAdjudicator.objects.filter(round=round.prev).count() if round.prev else None,
    }, {
        'type'      : "Venue",
        'total'     : round.tournament.venue_set.count(),
        'in_now'    : ActiveVenue.objects.filter(round=round).count(),
        'in_before' : ActiveVenue.objects.filter(round=round.prev).count() if round.prev else None,
    }]

    # Basic check before enable the button to advance
    if all([checks[0]['in_now'] > 1, checks[1]['in_now'] > 0, checks[2]['in_now'] > 0]):
        can_advance = True
    else:
        can_advance = False

    min_adjudicators = int(checks[0]['in_now'] / 2)
    min_venues = int(checks[0]['in_now'] / 2)

    return render(request, 'availability_index.html', dict(
        checkin_types=checks, can_advance=can_advance, previous_unconfirmed=previous_unconfirmed,
        min_adjudicators=min_adjudicators, min_venues=min_venues))


@admin_required
@round_view
def update_availability_all(request, round):
    round.activate_all()
    messages.add_message(
        request, messages.SUCCESS, 'Checked in all teams, adjudicators, and venues')
    return redirect_round('availability_index', round)


@admin_required
@round_view
def update_availability_previous(request, round):
    round.activate_previous()
    messages.add_message(request, messages.SUCCESS,
                         'Checked in all teams, adjudicators, and venues from previous round')
    return redirect_round('availability_index', round)


@admin_required
@round_view
def update_availability_breaking_adjs(request, round):
    round.activate_all_breaking_adjs()
    messages.add_message(
        request, messages.SUCCESS, 'Checked in all breaking adjudicators')
    return redirect_round('availability_index', round)


@admin_required
@round_view
def update_availability_breaking_teams(request, round):
    round.activate_all_breaking_teams()
    messages.add_message(
        request, messages.SUCCESS, 'Checked in all breaking teams')
    return redirect_round('availability_index', round)


@admin_required
@round_view
def update_availability_advancing_teams(request, round):
    round.activate_all_advancing_teams()
    messages.add_message(request, messages.SUCCESS,
        'Checked in all advancing teams')
    return redirect_round('availability_index', round)


def _availability(request, round, model, context_name):
    items = getattr(round, '%s_availability' % model)()
    context = {context_name: items}
    return render(request, '%s_availability.html' % model, context)


# Public (for barcode checkins)
@round_view
def checkin(request, round):
    context = {}
    if request.method == 'POST':
        v = request.POST.get('barcode_id')
        try:
            barcode_id = int(v)
            p = Person.objects.get(barcode_id=barcode_id)
            ch, created = Checkin.objects.get_or_create(
                person=p,
                round=round
            )
            context['person'] = p

        except (ValueError, Person.DoesNotExist):
            context['unknown_id'] = v

    return render(request, 'person_checkin.html', context)


# public (for barcode checkins)
@round_view
def post_checkin(request, round):
    v = request.POST.get('barcode_id')
    try:
        barcode_id = int(v)
        p = Person.objects.get(barcode_id=barcode_id)
        ch, created = Checkin.objects.get_or_create(
            person=p,
            round=round
        )

        message = p.checkin_message

        if not message:
            message = "Checked in %s" % p.name
        return HttpResponse(message)

    except (ValueError, Person.DoesNotExist):
        return HttpResponse("Unknown Id: %s" % v)


@round_view
def checkin_results(request, round, model, context_name):
    return _availability(request, round, model, context_name)


@admin_required
@round_view
def availability(request, round, model, context_name):
    return _availability(request, round, model, context_name)


def _update_availability(request, round, update_method, active_model, active_attr):
    if request.POST.get('copy'):
        prev_round = Round.objects.get(tournament=round.tournament,
                                       seq=round.seq-1)

        prev_objects = active_model.objects.filter(round=prev_round)
        available_ids = [getattr(o, '%s_id' % active_attr) for o in prev_objects]
        getattr(round, update_method)(available_ids)

        return HttpResponseRedirect(request.path.replace('update/', ''))

    available_ids = [int(a.replace("check_", "")) for a in list(request.POST.keys())
                     if a.startswith("check_")]

    # Calling the relevenat update method as defined in Round
    getattr(round, update_method)(available_ids)

    ACTION_TYPES = {
        ActiveVenue:       ActionLogEntry.ACTION_TYPE_AVAIL_VENUES_SAVE,
        ActiveTeam:        ActionLogEntry.ACTION_TYPE_AVAIL_TEAMS_SAVE,
        ActiveAdjudicator: ActionLogEntry.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE,
    }
    if active_model in ACTION_TYPES:
        ActionLogEntry.objects.log(type=ACTION_TYPES[active_model],
            user=request.user, round=round, tournament=round.tournament)

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
