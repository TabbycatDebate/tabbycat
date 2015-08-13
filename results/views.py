from debate.models import Debate, Round, Adjudicator, DebateAdjudicator
from motions.models import Motion
from action_log.models import ActionLog

from result import BallotSet
from forms import BallotSetForm

from utils import *
from models import *

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
    return r2r(request, "public_results_for_round.html", dict(
            draw=draw, show_motions_column=show_motions_column, show_splits=show_splits,
            show_ballots=show_ballots))



@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_results')
def public_results_index(request, tournament):
    rounds = Round.objects.filter(tournament=tournament,
        seq__lt=tournament.current_round.seq, silent=False).order_by('seq')
    return r2r(request, "public_results_index.html", dict(rounds=rounds))


@login_required
@tournament_view
def edit_ballotset(request, t, ballotsub_id):
    ballotsub = get_object_or_404(models.BallotSubmission, id=ballotsub_id)
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
        form = BallotSetForm(ballotsub, request.POST)

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
        form = BallotSetForm(ballotsub)

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
        return r2r(request, 'public_enter_results_error.html', dict(adjudicator=adjudicator,
                message='The draw and/or motions for the round haven\'t been released yet.'))
    try:
        da = DebateAdjudicator.objects.get(adjudicator=adjudicator, debate__round=round)
    except DebateAdjudicator.DoesNotExist:
        return r2r(request, 'public_enter_results_error.html', dict(adjudicator=adjudicator,
                message='It looks like you don\'t have a debate this round.'))

    ip_address = get_ip_address(request)
    ballotsub = models.BallotSubmission(debate=da.debate, ip_address=ip_address,
            submitter_type=BallotSubmission.SUBMITTER_PUBLIC)

    if request.method == 'POST':
        form = BallotSetForm(ballotsub, request.POST, password=True)
        if form.is_valid():
            form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_BALLOT_SUBMIT,
                    ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            return r2r(request, 'public_success.html', dict(success_kind="ballot"))
    else:
        form = BallotSetForm(ballotsub, password=True)

    context = {
        'form'                : form,
        'debate'              : da.debate,
        'round'               : round,
        'ballotsub'           : ballotsub,
        'adjudicator'         : adjudicator,
        'existing_ballotsubs' : da.debate.ballotsubmission_set.exclude(discarded=True).count(),
        'show_adj_contact'    : False,
    }
    return r2r(request, 'public_enter_results.html', context)


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
        form = BallotSetForm(ballotsub, request.POST)
        if form.is_valid():
            form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_BALLOT_CREATE, user=request.user,
                    ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            messages.success(request, "Ballot set for %s added." % debate.matchup)
            return redirect_round('results', debate.round)
    else:
        form = BallotSetForm(ballotsub)

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
    return r2r(request, 'public_ballot_set.html', dict(debate=debate, ballot_set=ballot_set))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_ballots')
def public_ballot_submit(request, t):
    r = t.current_round

    das = DebateAdjudicator.objects.filter(debate__round=r).select_related('adjudicator', 'debate')

    if r.draw_status == r.STATUS_RELEASED and r.motions_good_for_public:
        draw = r.get_draw()
        return r2r(request, 'public_add_ballot.html', dict(das=das))
    else:
        return r2r(request, 'public_add_ballot_unreleased.html', dict(das=None, round=r))