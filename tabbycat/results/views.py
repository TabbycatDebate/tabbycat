import json
import datetime
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.template import Context, Template
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_page

from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from participants.models import Adjudicator
from motions.models import Motion
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin
from tournaments.models import Round
from utils.views import admin_required, public_optional_tournament_view, round_view, tournament_view
from utils.misc import get_ip_address, redirect_round, reverse_tournament
from utils.mixins import HeadlessTemplateView, SuperuserRequiredMixin, VueTableMixin
from utils.tables import TabbycatTableBuilder
from venues.models import Venue

from .result import BallotSet
from .forms import BallotSetForm
from .models import BallotSubmission, TeamScore
from .mixins import DebateResultCellsMixin

logger = logging.getLogger(__name__)


@login_required
@tournament_view
def toggle_postponed(request, t, debate_id):
    debate = Debate.objects.get(pk=debate_id)
    if debate.result_status == debate.STATUS_POSTPONED:
        debate.result_status = debate.STATUS_NONE
    else:
        debate.result_status = debate.STATUS_POSTPONED

    debate.save()
    return redirect_round('results', debate.round)


class ResultsEntryForRoundView(RoundMixin, SuperuserRequiredMixin, VueTableMixin, DebateResultCellsMixin, TemplateView):

    template_name = 'results.html'
    sort_key = 'Status'
    draw = None

    def get_or_set_draw(self):
        if self.draw:
            return self.draw
        else:
            self.draw = self.get_round().get_draw()
            return self.draw

    def get_table_data(self):
        t = self.get_tournament()
        draw = self.get_or_set_draw()

        draw_data = []
        for d in draw:
            ddict = self.status_cells(d)
            ddict.extend(self.ballot_entry_cells(d, t))
            ddict.append({
                'head': {'tooltip': 'Bracket', 'key': 'B', 'icon': 'glyphicon-stats'},
                'cell': {'text': d.bracket}
            })
            ddict.extend(self.venue_cells(d, t))
            ddict.extend(self.team_cells(d.aff_team, t, key="affirmative", show_speakers=True, hide_institution=True))
            ddict.extend(self.team_cells(d.neg_team, t, key="negative", show_speakers=True, hide_institution=True))
            ddict.extend(self.adjudicators_cells(d, t, show_splits=True))
            draw_data.append(ddict)

        return draw_data

    def get_context_data(self, **kwargs):
        draw = self.get_or_set_draw()

        kwargs["stats"] = {
            'none': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=False).count(),
            'ballot_in': draw.filter(result_status=Debate.STATUS_NONE, ballot_in=True).count(),
            'draft': draw.filter(result_status=Debate.STATUS_DRAFT).count(),
            'confirmed': draw.filter(result_status=Debate.STATUS_CONFIRMED).count(),
            'postponed': draw.filter(result_status=Debate.STATUS_POSTPONED).count(),
        }

        return super().get_context_data(**kwargs)


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
        template = "assistant_results.html"
        draw = draw.filter(result_status__in=(
            Debate.STATUS_NONE, Debate.STATUS_DRAFT, Debate.STATUS_POSTPONED))
    else:
        template = "results.html"

    num_motions = Motion.objects.filter(round=round).count()
    show_motions_column = num_motions > 1
    has_motions = num_motions > 0

    return render(request, template, dict(draw=draw, stats=stats,
                  show_motions_column=show_motions_column, has_motions=has_motions))


class PublicResultsForRoundView(RoundMixin, PublicTournamentPageMixin, VueTableMixin, HeadlessTemplateView):

    public_page_preference = 'public_results'
    page_title = 'Results'
    page_emoji = '💥'
    sort_key = 'Team'

    def get_table(self):
        round = self.get_round()
        tournament = self.get_tournament()
        teamscores = TeamScore.objects.filter(debate_team__debate__round=round)
        debates = [ts.debate_team.debate for ts in teamscores]

        table = TabbycatTableBuilder(view=self, sort_key="Team")

        table.add_team_columns([ts.debate_team.team for ts in teamscores])

        if tournament.pref('ballots_released'):
            ballot_links_header = {'key': "Ballot", 'icon': 'glyphicon-search'}
            ballot_links_data = [{
                'text': "View Ballot",
                'link': reverse_tournament('public_ballots_view', tournament, kwargs={'debate_id': debate.id})
            } if debate else "" for debate in debates]
            table.add_column(ballot_links_header, ballot_links_data)

        results_data = []
        for ts in teamscores:
            opposition = ts.debate_team.opposition.team
            result = {'text': " vs " + opposition.short_name}
            if ts.win is True:
                result['icon'] = "glyphicon-arrow-up text-success"
                result['sort'] = 1
                result['tooltip'] = "Won against " + opposition.long_name
            elif ts.win is False:
                result['icon'] = "glyphicon-arrow-down text-danger"
                result['sort'] = 2
                result['tooltip'] = "Lost to " + opposition.long_name
            else: # None
                result['icon'] = ""
                result['sort'] = 3
                result['tooltip'] = "No result for debate against " + opposition.long_name
            results_data.append(result)
        table.add_column("Result", results_data)

        table.add_column("Side", [ts.debate_team.get_position_display() for ts in teamscores])
        table.add_debate_adjudicators_column(debates, show_splits=False)

        if tournament.pref('show_motions_in_results'):
            table.add_motion_column([debate.confirmed_ballot.motion for debate in debates])

        return table

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        round = self.get_round()
        if round.silent:
            logger.info("Refused results for %s: silent", round.name)
            return render(request, 'public_results_silent.html')
        if round.seq >= tournament.current_round.seq and not tournament.release_all:
            logger.info("Refused results for %s: not yet available", round.name)
            return render(request, 'public_results_not_available.html')
        return super().get(request, *args, **kwargs)


class PublicResultsIndexView(PublicTournamentPageMixin, TemplateView):

    template_name = 'public_results_index.html'
    public_page_preference = 'public_results'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs["rounds"] = tournament.round_set.filter(
            seq__lt=tournament.current_round.seq,
            silent=False).order_by('seq')
        return super().get_context_data(**kwargs)


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
        form = BallotSetForm(ballotsub, request.POST)

        if form.is_valid():
            form.save()

            if ballotsub.discarded:
                action_type = ActionLogEntry.ACTION_TYPE_BALLOT_DISCARD
                messages.success(request, "Ballot set for %s discarded." % debate.matchup)
            elif ballotsub.confirmed:
                ballotsub.confirmer = request.user
                ballotsub.confirm_timestamp = datetime.datetime.now()
                ballotsub.save()
                action_type = ActionLogEntry.ACTION_TYPE_BALLOT_CONFIRM
                messages.success(request, "Ballot set for %s confirmed." % debate.matchup)
            else:
                action_type = ActionLogEntry.ACTION_TYPE_BALLOT_EDIT
                messages.success(request, "Edits to ballot set for %s saved." % debate.matchup)
            ActionLogEntry.objects.log(type=action_type, user=request.user, ballot_submission=ballotsub,
                                       ip_address=get_ip_address(request), tournament=t)

            return redirect_round('results', debate.round)
    else:
        form = BallotSetForm(ballotsub)

    template = 'enter_results.html' if request.user.is_superuser else 'assistant_enter_results.html'
    context = {
        'form'             : form,
        'ballotsub'        : ballotsub,
        'debate'           : debate,
        'all_ballotsubs'   : all_ballotsubs,
        'disable_confirm'  : request.user == ballotsub.submitter and not t.pref('disable_ballot_confirms') and not request.user.is_superuser,
        'round'            : debate.round,
        'not_singleton'    : all_ballotsubs.exclude(id=ballotsub_id).exists(),
        'new'              : False,
    }
    return render(request, template, context)


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
        return render(request, 'public_enter_results_error.html', dict(
            adjudicator=adjudicator, message='The draw and/or motions for the '
            'round haven\'t been released yet.'))

    try:
        da = DebateAdjudicator.objects.get(adjudicator=adjudicator, debate__round=round)
    except DebateAdjudicator.DoesNotExist:
        return render(request, 'public_enter_results_error.html', dict(
            adjudicator=adjudicator,
            message='It looks like you don\'t have a debate this round.'))

    ip_address = get_ip_address(request)
    ballotsub = BallotSubmission(
        debate=da.debate, ip_address=ip_address,
        submitter_type=BallotSubmission.SUBMITTER_PUBLIC)

    if request.method == 'POST':
        form = BallotSetForm(ballotsub, request.POST, password=True)
        if form.is_valid():
            form.save()
            ActionLogEntry.objects.log(
                type=ActionLogEntry.ACTION_TYPE_BALLOT_SUBMIT,
                ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            return render(request, 'public_success.html', dict(success_kind="ballot"))
    else:
        form = BallotSetForm(ballotsub, password=True)

    context = {
        'form'                : form,
        'debate'              : da.debate,
        'round'               : round,
        'ballotsub'           : ballotsub,
        'adjudicator'         : adjudicator,
        'existing_ballotsubs' : da.debate.ballotsubmission_set.exclude(discarded=True).count(),
    }
    return render(request, 'public_enter_results.html', context)


@login_required
@tournament_view
def new_ballotset(request, t, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    ip_address = get_ip_address(request)
    ballotsub = BallotSubmission(debate=debate, submitter=request.user,
                                 submitter_type=BallotSubmission.SUBMITTER_TABROOM,
                                 ip_address=ip_address)

    if not debate.adjudicators.has_chair:
        messages.error(request, "Whoops! The debate %s doesn't have a chair, "
                       "so you can't enter results for it." % debate.matchup)
        return redirect_round('results', debate.round)

    if request.method == 'POST':
        form = BallotSetForm(ballotsub, request.POST)
        if form.is_valid():
            form.save()
            ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_BALLOT_CREATE, user=request.user,
                                       ballot_submission=ballotsub, ip_address=ip_address, tournament=t)
            messages.success(request, "Ballot set for %s added." % debate.matchup)
            return redirect_round('results', debate.round)
    else:
        form = BallotSetForm(ballotsub)

    template = 'enter_results.html' if request.user.is_superuser else 'assistant_enter_results.html'
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
    }
    return render(request, template, context)


@login_required
@tournament_view
def ballots_status(request, t):
    # Draw Status for Tournament Homepage
    intervals = 20

    def minutes_ago(time):
        time_difference = datetime.datetime.now() - time
        minutes_ago = time_difference.days * 1440 + time_difference.seconds / 60
        return minutes_ago

    ballots = list(BallotSubmission.objects.filter(debate__round=t.current_round).order_by('timestamp'))
    debates = Debate.objects.filter(round=t.current_round).count()
    if len(ballots) is 0:
        return HttpResponse(json.dumps([]), content_type="text/json")

    start_entry = minutes_ago(ballots[0].timestamp)
    end_entry = minutes_ago(ballots[-1].timestamp)
    chunks = (end_entry - start_entry) / intervals

    stats = []
    for i in range(intervals + 1):
        time_period = (i * chunks) + start_entry
        stat = [int(time_period), debates, 0, 0]
        for b in ballots:
            if minutes_ago(b.timestamp) >= time_period:
                if b.debate.result_status == Debate.STATUS_DRAFT:
                    stat[2] += 1
                    stat[1] -= 1
                elif b.debate.result_status == Debate.STATUS_CONFIRMED:
                    stat[3] += 1
                    stat[1] -= 1
        stats.append(stat)

    return HttpResponse(json.dumps(stats), content_type="text/json")


@login_required
@tournament_view
def latest_results(request, t):
    # Latest Results for Tournament Homepage
    results_objects = []
    ballots = BallotSubmission.objects.filter(
        debate__round__tournament=t, confirmed=True).order_by(
        '-timestamp')[:15].select_related('debate')
    timestamp_template = Template("{% load humanize %}{{ t|naturaltime }}")
    for b in ballots:
        if b.ballot_set.winner == b.ballot_set.debate.aff_team:
            winner = b.ballot_set.debate.aff_team.short_name + " (Aff)"
            looser = b.ballot_set.debate.neg_team.short_name + " (Neg)"
        else:
            winner = b.ballot_set.debate.neg_team.short_name + " (Neg)"
            looser = b.ballot_set.debate.aff_team.short_name + " (Aff)"

        results_objects.append({
            'user': winner + " won vs " + looser,
            'timestamp': timestamp_template.render(Context({'t': b.timestamp})),
        })

    return HttpResponse(json.dumps(results_objects), content_type="text/json")


@admin_required
@round_view
def ballot_checkin(request, round):
    ballots_left = ballot_checkin_number_left(round)
    return render(request, 'ballot_checkin.html', dict(ballots_left=ballots_left))


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
    except DebateBallotCheckinError as e:
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
    except DebateBallotCheckinError as e:
        data = {'exists': False, 'message': str(e)}
        return HttpResponse(json.dumps(data))

    debate.ballot_in = True
    debate.save()

    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_BALLOT_CHECKIN,
                               user=request.user, debate=debate,
                               tournament=round.tournament)

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
    return render(request, 'public_ballot_set.html', dict(debate=debate, ballot_set=ballot_set))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_ballots')
def public_ballot_submit(request, t):
    r = t.current_round

    das = DebateAdjudicator.objects.filter(debate__round=r).select_related('adjudicator', 'debate')

    if r.draw_status == r.STATUS_RELEASED and r.motions_good_for_public:
        return render(request, 'public_add_ballot.html', dict(das=das))
    else:
        return render(request, 'public_add_ballot_unreleased.html', dict(das=None, round=r))
