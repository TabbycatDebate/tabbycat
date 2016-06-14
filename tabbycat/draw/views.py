import datetime
import json
import logging

from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.shortcuts import render

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjfeedback.models import AdjudicatorFeedbackQuestion
from breakqual.models import BreakingTeam
from motions.models import Motion
from participants.models import Team
from standings.teams import TeamStandingsGenerator
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin
from tournaments.models import Division, Round, Tournament
from utils.mixins import CacheMixin, PostOnlyRedirectView, SuperuserRequiredMixin, VueTableMixin
from utils.misc import reverse_round
from utils.views import admin_required, expect_post
from utils.views import public_optional_tournament_view, redirect_round, round_view, tournament_view
from venues.models import Venue, VenueGroup
from venues.allocator import allocate_venues

from .manager import DrawManager
from .models import Debate, DebateTeam, TeamPositionAllocation

logger = logging.getLogger(__name__)


TPA_MAP = {
    TeamPositionAllocation.POSITION_AFFIRMATIVE: "Aff",
    TeamPositionAllocation.POSITION_NEGATIVE: "Neg",
    None: "-"
}


# ==============================================================================
# Viewing Draw
# ==============================================================================

class DrawTablePage(RoundMixin, TemplateView, VueTableMixin):

    template_name = 'draw_display_by.html'
    sort_key = 'Venue'

    def create_row(self, d, t, sort_key=None, sort_value=None):
        ddict = []
        if sort_key and sort_value:
            ddict.append((sort_key, sort_value))

        ddict.extend(self.venue_cells(d, t, with_times=True))
        ddict.extend(self.team_cells(d.aff_team, t))
        ddict.extend(self.team_cells(d.neg_team, t))

        if t.pref('enable_division_motions'):
            ddict.append(('motion', [m.reference for m in d.division_motions]))
        if not t.pref('enable_divisions'):
            ddict.extend(self.adjudicators_cells(d, t, show_splits=False))

        return ddict

    def get_context_data(self, **kwargs):
        kwargs['round'] = self.get_round()
        return super().get_context_data(**kwargs)

    def get_table_data(self):
        round = self.get_round()
        draw = round.get_draw()
        t = self.get_tournament()
        if self.sorting is 'team':
            draw_data = []
            for d in draw:
                aff_row = self.create_row(d, t, 'Team', d.aff_team.short_name)
                neg_row = self.create_row(d, t, 'Team', d.neg_team.short_name)
                draw_data.extend([aff_row, neg_row])
        else:
            draw_data = [self.create_row(debate, t) for debate in draw]

        return draw_data


# ==============================================================================
# Creating Draw
# ==============================================================================

class PublicDrawForRound(DrawTablePage, PublicTournamentPageMixin, CacheMixin):

    public_page_preference = 'public_draw'
    sorting = 'venue'

    def get_template_names(self):
        round = self.get_round()
        if round.draw_status != round.STATUS_RELEASED:
            return ["public_draw_unreleased.html"]
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        round = self.get_round()
        if round.draw_status != round.STATUS_RELEASED:
            kwargs["round"] = self.get_round()
            return super(DrawTablePage, self).get_context_data(**kwargs) # skip DrawTablePage
        else:
            return super().get_context_data(**kwargs)


class PublicDrawForCurrentRound(PublicDrawForRound):

    def get_round(self):
        return self.get_tournament().current_round


class AdminDrawForRoundByVenue(DrawTablePage, LoginRequiredMixin):
    sorting = 'venue'


class AdminDrawForRoundByTeam(DrawTablePage, LoginRequiredMixin):
    sorting = 'team'


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
            return render(request,
                          "public_draw_released.html",
                          draw=draw, round=round)
        else:
            return render(request, 'public_draw_unreleased.html', dict(
                          'public_draw_unreleased.html',
                          draw=None, round=round))

    raise


def assistant_draw(request, round):
    if round.draw_status == round.STATUS_RELEASED:
        return draw_confirmed(request, round)


def get_draw_with_standings(round):
    draw = round.get_draw()

    if round.prev is None:
        return None, draw

    teams = round.tournament.team_set.select_related('institution')
    metrics = round.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'))
    standings = generator.generate(teams, round=round.prev)

    for debate in draw:
        aff_standing = standings.get_standing(debate.aff_team)
        neg_standing = standings.get_standing(debate.neg_team)
        debate.metrics = [(a, n) for a, n in zip(aff_standing.itermetrics(), neg_standing.itermetrics())]
        if round.is_break_round:
            debate.aff_breakrank = BreakingTeam.objects.get(
                break_category=round.break_category,
                team=debate.aff_team.id).break_rank
            debate.neg_breakrank = BreakingTeam.objects.get(
                break_category=round.break_category,
                team=debate.neg_team.id).break_rank
        else:
            if "points" in standings.metric_keys:
                debate.aff_is_pullup = abs(aff_standing.metrics["points"] - debate.bracket) >= 1
                debate.neg_is_pullup = abs(neg_standing.metrics["points"] - debate.bracket) >= 1
            debate.aff_subrank = aff_standing.rankings["subrank"]
            debate.neg_subrank = neg_standing.rankings["subrank"]

    return standings, draw


def draw_none(request, round):
    all_teams_count = Team.objects.filter(tournament=round.tournament).count()
    active_teams = round.active_teams.all()
    active_venues_count = round.active_venues.count()
    active_adjs = round.active_adjudicators.count()
    rooms = float(active_teams.count()) // 2
    if round.prev:
        previous_unconfirmed = round.prev.get_draw().filter(
            result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    else:
        previous_unconfirmed = 0

    return render(
        request, "draw_none.html", dict(
            active_teams=active_teams,
            active_venues_count=active_venues_count,
            active_adjs=active_adjs,
            rooms=rooms,
            round=round,
            previous_unconfirmed=previous_unconfirmed,
            all_teams_count=all_teams_count))


def draw_draft(request, round):
    standings, draw = get_draw_with_standings(round)
    return render(request, "draw_draft.html", dict(
        draw=draw, standings=standings))


def draw_confirmed(request, round):
    draw = round.cached_draw
    rooms = float(round.active_teams.count()) // 2
    active_adjs = round.active_adjudicators.all()

    return render(request, "draw_confirmed.html", dict(
                  draw=draw, active_adjs=active_adjs, rooms=rooms))


@admin_required
@round_view
def draw_with_standings(request, round):
    standings, draw = get_draw_with_standings(round)
    return render(request, "draw_with_standings.html", dict(
        draw=draw, standings=standings))


class CreateDrawView(LogActionMixin, SuperuserRequiredMixin, RoundMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_CREATE

    def get_redirect_url(self):
        return reverse_round('draw', self.get_round())

    def post(self, request, *args, **kwargs):
        round = self.get_round()

        if round.draw_status != round.STATUS_NONE:
            messages.error(request, "Could not create draw for {}, there was already a draw!".format(round.name))
            return super().post(request, *args, **kwargs)

        manager = DrawManager(round)
        manager.create()

        allocate_venues(round)

        self.log_action()
        return super().post(request, *args, **kwargs)


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


@round_view
def draw_confirm_regenerate(request, round):
    return render(request, "draw_confirm_regeneration.html", dict())


@admin_required
@expect_post
@round_view
def draw_regenerate(request, round):
    from .dbutils import delete_round_draw
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DRAW_REGENERATE,
                               user=request.user,
                               round=round,
                               tournament=round.tournament)
    delete_round_draw(round)
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
    for tpa in TeamPositionAllocation.objects.all():
        tpas[(tpa.team.id, tpa.round.seq)] = TPA_MAP[tpa.position]
    for team in teams:
        team.side_allocations = [tpas.get(
            (team.id, round.id), "-") for round in rounds]
    return render(request, "side_allocations.html", dict(
        teams=teams, rounds=rounds))


class SetRoundStartTimeView(SuperuserRequiredMixin, LogActionMixin, RoundMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ROUND_START_TIME_SET

    def get_redirect_url(self):
        return reverse_round('draw', self.get_round())

    def post(self, request, *args, **kwargs):
        time_text = request.POST["start_time"]
        try:
            time = datetime.datetime.strptime(time_text, "%H:%M").time()
        except ValueError:
            messages.error(request, "Sorry, \"{}\" isn't a valid time. It must "
                           "be in 24-hour format, with a colon, for "
                           "example: \"13:57\".".format(time_text))
            return super().post(request, *args, **kwargs)

        round = self.get_round()
        round.starts_at = time
        round.save()
        # Need to call explicitly, since this isn't a form view
        self.log_action()

        return super().post(request, *args, **kwargs)


@admin_required
@round_view
def schedule_debates(request, round):
    venue_groups = VenueGroup.objects.all()
    divisions = Division.objects.filter(tournament=round.tournament).order_by('id')
    return render(request, "draw_set_debate_times.html", dict(
        venue_groups=venue_groups, divisions=divisions))


@admin_required
@expect_post
@round_view
def apply_schedule(request, round):
    import datetime
    debates = Debate.objects.filter(round=round)
    for debate in debates:
        division = debate.teams[0].division
        if division and division.time_slot:
            date = request.POST[str(division.venue_group.id)]
            if date:
                time = "%s %s" % (date, division.time_slot)
                try:
                    debate.time = datetime.datetime.strptime(
                        time, "%Y-%m-%d %H:%M:%S")  # Chrome
                except ValueError:
                    debate.time = datetime.datetime.strptime(
                        time, "%d/%m/%Y %H:%M:%S")  # Others

                debate.save()

    messages.success(request, "Applied schedules to debates")
    return redirect_round('draw', round)


@admin_required
@round_view
def draw_matchups_edit(request, round):
    standings, draw = get_draw_with_standings(round)
    unused_teams = round.unused_teams()
    possible_debates = len(unused_teams) // 2 + 1  # The blank rows to add
    possible_debates = [None] * possible_debates
    return render(request, "draw_matchups_edit.html", dict(
        draw=draw, standings=standings, possible_debates=possible_debates,
        unused_teams=unused_teams))


@admin_required
@expect_post
@round_view
def save_matchups(request, round):
    # TODO: move to draws app
    # print request.POST.keys()

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


# ==============================================================================
# Public Draw Views
# ==============================================================================

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def public_all_draws(request, t):
    all_rounds = list(Round.objects.filter(
        tournament=t, draw_status=Round.STATUS_RELEASED))
    for r in all_rounds:
        r.draw = r.get_draw()

    return render(request, 'public_draw_display_all.html', dict(
        all_rounds=all_rounds))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_side_allocations')
def public_side_allocations(request, t):
    # TODO: move to draws app
    teams = Team.objects.filter(tournament=t)
    rounds = Round.objects.filter(tournament=t).order_by("seq")
    tpas = dict()
    for tpa in TeamPositionAllocation.objects.all():
        tpas[(tpa.team.id, tpa.round.seq)] = TPA_MAP[tpa.position]
    for team in teams:
        team.side_allocations = [tpas.get(
            (team.id, round.id), "-") for round in rounds]
    return render(request, "side_allocations.html", dict(
        teams=teams, rounds=rounds))


@login_required
@round_view
def confirmations_view(request, round):
    from participants.models import Adjudicator
    from adjallocation.models import DebateAdjudicator
    adjs = Adjudicator.objects.all().order_by('name')
    for adj in adjs:
        shifts = DebateAdjudicator.objects.filter(adjudicator=adj, debate__round__tournament__active=True)
        if len(shifts) > 0:
            adj.shifts = shifts

    return render(request, 'confirmations_view.html', dict(adjs=adjs))


# Mastersheets
@login_required
@round_view
def master_sheets_list(request, round):
    venue_groups = VenueGroup.objects.all()
    return render(request, 'division_sheets_list.html', dict(
        venue_groups=venue_groups))


@login_required
@round_view
def master_sheets_view(request, round, venue_group_id):
    # Temporary - pre unified venue groups
    base_venue_group = VenueGroup.objects.get(id=venue_group_id)
    active_tournaments = Tournament.objects.filter(active=True)

    for tournament in list(active_tournaments):
        tournament.debates = Debate.objects.select_related(
            'division', 'division__venue_group__short_name', 'round',
            'round__tournament').filter(
                # All Debates, with a matching round, at the same venue group name
                round__seq=round.seq,
                round__tournament=tournament,
                # Hack - remove when venue groups are unified
                division__venue_group__short_name=base_venue_group.short_name
        ).order_by('round', 'division__venue_group__short_name', 'division')

    return render(request, 'printing/master_sheets_view.html', dict(
        base_venue_group=base_venue_group, active_tournaments=active_tournaments))


@login_required
@round_view
def room_sheets_view(request, round, venue_group_id):
    # Temporary - pre unified venue groups
    base_venue_group = VenueGroup.objects.get(id=venue_group_id)
    venues = Venue.objects.filter(group=base_venue_group)

    for venue in venues:
        venue.debates = Debate.objects.filter(
            # All Debates, with a matching round, at the same venue group name
            round__seq=round.seq,
            venue=venue
        ).select_related('round__tournament__short_name').order_by('round__tournament__seq')

    return render(request, 'printing/room_sheets_view.html', dict(
        base_venue_group=base_venue_group, venues=venues))


class PrintFeedbackFormsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'printing/feedback_list.html'

    def team_on_orallist(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, chair_on_panellist=True).exists()

    def chair_on_panellist(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, panellist_on_chair=True).exists()

    def panellist_on_panellist(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, panellist_on_panellist=True).exists()

    def panellist_on_chair(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, team_on_orallist=True).exists()

    def questions_json_dict(self):
        questions = []
        for q in self.get_round().tournament.adj_feedback_questions:
            q_set = {
                'text': q.text, 'seq': q.seq, 'type': q.answer_type,
                'required': json.dumps(q.answer_type),
                'chair_on_panellist': json.dumps(q.chair_on_panellist),
                'panellist_on_chair': json.dumps(q.panellist_on_chair),
                'panellist_on_panellist': json.dumps(q.panellist_on_panellist),
                'team_on_orallist': json.dumps(q.team_on_orallist),
            }
            if q.choices:
                q_set['choice_options'] = q.choices.split("//")
            elif q.min_value is not None and q.max_value is not None:
                q_set['choice_options'] = q.choices_for_number_scale

            questions.append(q_set)
        return questions

    def construct_info(self, venue, source, source_p, target, target_p):
        source_n = source.name if hasattr(source, 'name') else source.short_name
        return {
            'room': venue.name,
            'authorInstitution': source.institution.code,
            'author': source_n, 'authorPosition': source_p,
            'target': target.name, 'targetPosition': target_p
        }

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.questions_json_dict()
        kwargs['ballots'] = []

        for debate in self.get_round().get_draw_by_room():
            chair = debate.adjudicators.chair

            if self.team_on_orallist():
                for team in debate.teams:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, team, "Team", chair, "C"))

            if self.chair_on_panellist():
                for adj in debate.adjudicators.panel:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, chair, "C", adj, "P"))
                for adj in debate.adjudicators.trainees:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, chair, "C", adj, "T"))

            if self.panellist_on_chair():
                for adj in debate.adjudicators.panel:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, adj, "P", chair, "C"))
                for adj in debate.adjudicators.trainees:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, adj, "T", chair, "C"))

        return super().get_context_data(**kwargs)


class PrintScoreSheetsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'printing/scoresheet_list.html'

    def get_context_data(self, **kwargs):
        kwargs['motions'] = Motion.objects.filter(round=self.get_round()).values('text').order_by('seq')
        kwargs['ballots'] = []

        for debate in self.get_round().get_draw_by_room():
            debate_info = {
                'room': debate.venue.name if debate.venue else 'TBA',
                'aff': debate.aff_team.short_name,
                'affEmoji': debate.aff_team.emoji,
                'affSpeakers': [s.name for s in debate.aff_team.speakers],
                'neg': debate.neg_team.short_name,
                'negEmoji': debate.neg_team.emoji,
                'negSpeakers': [s.name for s in debate.neg_team.speakers],
                'panel': []
            }
            for position, adj in debate.adjudicators:
                debate_info['panel'].append({
                    'name': adj.name,
                    'institution': adj.institution.code,
                    'position': position
                })

            if len(debate_info['panel']) is 0:
                ballot_data = {
                    'author': "_______________________________________________",
                    'authorInstitution': "",
                    'authorPosition': "",
                }
                ballot_data.update(debate_info)  # Extend with debateInfo keys
                kwargs['ballots'].append(ballot_data)
            else:
                for adj in (a for a in debate_info['panel'] if a['position'] != "T"):
                    ballot_data = {
                        'author': adj['name'],
                        'authorInstitution': adj['institution'],
                        'authorPosition': adj['position'],
                    }
                    ballot_data.update(debate_info)  # Extend with debateInfo keys
                    kwargs['ballots'].append(ballot_data)

        return super().get_context_data(**kwargs)
