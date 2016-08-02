from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic.base import TemplateView, View

from adjallocation.models import DebateAdjudicator
from adjfeedback.progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam
from draw.prefetch import populate_opponents, populate_teams
from results.models import TeamScore
from results.prefetch import populate_confirmed_ballots, populate_wins
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.mixins import CacheMixin, SingleObjectByRandomisedUrlMixin, SingleObjectFromTournamentMixin
from utils.mixins import ModelFormSetView, SuperuserRequiredMixin, VueTableTemplateView
from utils.tables import TabbycatTableBuilder

from .models import Adjudicator, Institution, Speaker, Team


class TeamSpeakersJsonView(CacheMixin, SingleObjectFromTournamentMixin, View):

    model = Team
    pk_url_kwarg = 'team_id'
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get(self, request, *args, **kwargs):
        team = self.get_object()
        speakers = team.speakers
        data = {i: "<li>" + speaker.name + "</li>" for i, speaker in enumerate(speakers)}
        return JsonResponse(data, safe=False)


class PublicParticipantsListView(PublicTournamentPageMixin, CacheMixin, VueTableTemplateView):

    public_page_preference = 'public_participants'
    page_title = 'Participants'
    page_emoji = '🚌'

    def get_tables(self):
        t = self.get_tournament()

        adjudicators = t.adjudicator_set.select_related('institution')
        adjs_table = TabbycatTableBuilder(view=self, title="Adjudicators", sort_key="Name")
        adjs_table.add_adjudicator_columns(adjudicators)

        speakers = Speaker.objects.filter(team__tournament=t).select_related(
                'team', 'team__institution').prefetch_related('team__speaker_set')
        speakers_table = TabbycatTableBuilder(view=self, title="Speakers", sort_key="Name")
        speakers_table.add_speaker_columns(speakers)
        speakers_table.add_team_columns([speaker.team for speaker in speakers])

        return [adjs_table, speakers_table]


# ==============================================================================
# Team and adjudicator record pages
# ==============================================================================

class ParticipantRecordsListView(SuperuserRequiredMixin, TournamentMixin, VueTableTemplateView):

    page_title = 'Team and Adjudicator Record Pages'
    page_emoji = '🌸'

    def get_tables(self):
        t = self.get_tournament()

        adjudicators = t.adjudicator_set.select_related('institution')
        adjs_table = TabbycatTableBuilder(view=self, title="Adjudicators", sort_key="Name")
        adjs_table.add_adjudicator_columns(adjudicators)

        teams = t.team_set.select_related('institution')
        teams_table = TabbycatTableBuilder(view=self, title="Teams", sort_key="Name")
        teams_table.add_team_columns(teams, key="Name")

        return [adjs_table, teams_table]


class BaseRecordView(SingleObjectFromTournamentMixin, VueTableTemplateView):

    def get_context_data(self, **kwargs):
        kwargs['admin_page'] = self.admin
        kwargs['draw_released'] = self.get_tournament().current_round.draw_status == Round.STATUS_RELEASED
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class BaseTeamRecordView(BaseRecordView):

    model = Team
    template_name = 'team_record.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()

        try:
            kwargs['debateteam'] = self.object.debateteam_set.get(
                debate__round=tournament.current_round)
        except ObjectDoesNotExist:
            kwargs['debateteam'] = None

        kwargs['page_title'] = 'Record for ' + self.object.long_name
        if tournament.pref('show_emoji'):
            kwargs['page_emoji'] = self.object.emoji

        kwargs['feedback_progress'] = FeedbackProgressForTeam(self.object, tournament)

        return super().get_context_data(**kwargs)

    def get_table(self):
        """On team record pages, the table is the results table."""
        tournament = self.get_tournament()
        teamscores = TeamScore.objects.filter(debate_team__team=self.object,
                ballot_submission__confirmed=True,
                debate_team__debate__round__seq__lt=tournament.current_round.seq,
                debate_team__debate__round__draw_status=Round.STATUS_RELEASED,
                debate_team__debate__round__silent=False).select_related(
                'debate_team__debate', 'debate_team__debate__round').prefetch_related(
                'debate_team__debate__debateadjudicator_set__adjudicator')
        debates = [ts.debate_team.debate for ts in teamscores]
        populate_opponents([ts.debate_team for ts in teamscores])
        populate_confirmed_ballots(debates, motions=True, ballotsets=True)

        table = TabbycatTableBuilder(view=self, title="Results", sort_key="Round")
        table.add_round_column([debate.round for debate in debates])
        table.add_debate_result_by_team_columns(teamscores)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if self.admin or tournament.pref('public_motions'):
            table.add_motion_column([debate.confirmed_ballot.motion
                if debate.confirmed_ballot else None for debate in debates])

        table.add_debate_ballot_link_column(debates)

        return table


class BaseAdjudicatorRecordView(BaseRecordView):

    model = Adjudicator
    template_name = 'adjudicator_record.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()

        try:
            kwargs['debateadjudicator'] = self.object.debateadjudicator_set.get(
                debate__round=tournament.current_round)
        except ObjectDoesNotExist:
            kwargs['debateadjudicator'] = None

        kwargs['page_title'] = 'Record for ' + self.object.name
        kwargs['page_emoji'] = '⚖'
        kwargs['feedback_progress'] = FeedbackProgressForAdjudicator(self.object, tournament)

        return super().get_context_data(**kwargs)

    def get_table(self):
        """On adjudicator record pages, the table is the previous debates table."""
        tournament = self.get_tournament()
        debateadjs = DebateAdjudicator.objects.filter(adjudicator=self.object,
                debate__round__seq__lt=tournament.current_round.seq,
                debate__round__draw_status=Round.STATUS_RELEASED,
                debate__round__silent=False).select_related(
                'debate', 'debate__round').prefetch_related(
                'debate__debateadjudicator_set', 'debate__debateadjudicator_set__adjudicator')
        debates = [da.debate for da in debateadjs]
        populate_teams(debates)
        populate_wins(debates)
        populate_confirmed_ballots(debates, motions=True, ballotsets=True)

        table = TabbycatTableBuilder(view=self, title="Previous Rounds", sort_key="Round")
        table.add_round_column([debate.round for debate in debates])
        table.add_debate_results_columns(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True, highlight_adj=self.object)

        if self.admin or tournament.pref('public_motions'):
            table.add_motion_column([debate.confirmed_ballot.motion
                if debate.confirmed_ballot else None for debate in debates])

        table.add_debate_ballot_link_column(debates)
        return table


class TeamRecordView(SuperuserRequiredMixin, BaseTeamRecordView):
    admin = True


class AdjudicatorRecordView(SuperuserRequiredMixin, BaseAdjudicatorRecordView):
    admin = True


class PublicTeamRecordView(PublicTournamentPageMixin, BaseTeamRecordView):
    public_page_preference = 'public_record'
    admin = False


class PublicAdjudicatorRecordView(PublicTournamentPageMixin, BaseAdjudicatorRecordView):
    public_page_preference = 'public_record'
    admin = False


# ==============================================================================
# Cross-tournament views
# ==============================================================================

class AllTournamentsAllInstitutionsView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'enable_mass_draws'
    template_name = 'public_all_tournament_institutions.html'

    def get_context_data(self, **kwargs):
        kwargs['institutions'] = Institution.objects.all()
        return super().get_context_data(**kwargs)


class AllTournamentsAllTeamsView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'enable_mass_draws'
    template_name = 'public_all_tournament_teams.html'

    def get_context_data(self, **kwargs):
        kwargs['teams'] = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
        return super().get_context_data(**kwargs)


# ==============================================================================
# Shift scheduling
# ==============================================================================

class PublicConfirmShiftView(SingleObjectByRandomisedUrlMixin, PublicTournamentPageMixin, ModelFormSetView):
    # Django doesn't have a class-based view for formsets, so this implements
    # the form processing analogously to FormView, with less decomposition.
    # See also: motions.views.EditMotionsView.

    public_page_preference = 'allocation_confirmations'
    template_name = 'confirm_shifts.html'
    formset_factory_kwargs = dict(can_delete=False, extra=0, fields=['timing_confirmed'])
    model = Adjudicator
    formset_model = DebateAdjudicator

    def get_success_url(self):
        return reverse_tournament('participants-public-confirm-shift',
                self.get_tournament(), kwargs={'url_key': self.object.url_key})

    def get_formset_queryset(self):
        return self.object.debateadjudicator_set.all()

    def get_context_data(self, **kwargs):
        kwargs['adjudicator'] = self.get_object()
        return super().get_context_data(**kwargs)

    def formset_valid(self, formset):
        messages.success(self.request, "Your shift check-ins have been saved")
        return super().formset_valid(formset)

    def formset_invalid(self, formset):
        messages.error(self.request, "Whoops! There was a problem with the form.")
        return super().formset_invalid(formset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
