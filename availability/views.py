from debate.models import Round
from participants.models import Person
from action_log.models import ActionLog

from utils import *

def _availability(request, round, model, context_name):

    items = getattr(round, '%s_availability' % model)()

    context = {
        context_name: items,
    }

    return r2r(request, '%s_availability.html' % model, context)

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

# public (for barcode checkins)
# public
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

    available_ids = [int(a.replace("check_", "")) for a in request.POST.keys()
                     if a.startswith("check_")]

    # Calling the relevenat update method as defined in Round
    getattr(round, update_method)(available_ids)

    ACTION_TYPES = {
        ActiveVenue:       ActionLog.ACTION_TYPE_AVAIL_VENUES_SAVE,
        ActiveTeam:        ActionLog.ACTION_TYPE_AVAIL_TEAMS_SAVE,
        ActiveAdjudicator: ActionLog.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE,
    }
    if active_model in ACTION_TYPES:
        ActionLog.objects.log(type=ACTION_TYPES[active_model],
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
