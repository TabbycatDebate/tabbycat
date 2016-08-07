from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView

from participants.models import Adjudicator
from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from utils.misc import reverse_tournament
from utils.mixins import (CacheMixin, PostOnlyRedirectView, SingleObjectFromTournamentMixin,
                          SuperuserRequiredMixin, VueTableTemplateView)
from utils.tables import TabbycatTableBuilder
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import BreakCategory, BreakingTeam
from .generator import BreakGenerator
from . import forms
from . import breaking


class PublicBreakIndexView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'public_results'
    template_name = 'public_break_index.html'


class PublicBreakingTeamsView(SingleObjectFromTournamentMixin, PublicTournamentPageMixin, CacheMixin, VueTableTemplateView):

    public_page_preference = 'public_breaking_teams'
    page_emoji = '👑'
    model = BreakCategory
    slug_url_kwarg = 'category'

    def get_table(self):
        t = self.get_tournament()

        standings = breaking.get_breaking_teams(self.object, include_all=True, include_categories=t.pref('public_break_categories'))

        table = TabbycatTableBuilder(view=self, title=self.object.name)
        table.add_ranking_columns(standings)
        table.add_column("Break", [standing.break_rank for standing in standings])
        table.add_team_columns([info.team for info in standings])
        table.add_metric_columns(standings)
        return table

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class AdminBreakIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = 'breaking_index.html'


class BreakingTeamsFormView(LogActionMixin, SuperuserRequiredMixin, SingleObjectFromTournamentMixin, FormView):
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_EDIT_REMARKS
    model = BreakCategory
    slug_url_kwarg = 'category'
    form_class = forms.BreakingTeamsForm
    template_name = 'breaking_teams.html'

    def get_context_data(self, **kwargs):
        kwargs['generated'] = BreakingTeam.objects.filter(
                break_category__tournament=self.get_tournament()).exists()
        kwargs['category'] = self.object
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.object
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Changes to breaking team remarks saved.")
        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class UpdateAllBreaksView(LogActionMixin, TournamentMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ALL
    success_message = "Teams break updated for all break categories."
    tournament_redirect_pattern_name = 'breakqual-teams'

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        for category in tournament.breakcategory_set.order_by('-priority'):
            BreakGenerator(category).generate()
        messages.success(request, self.success_message)
        self.log_action()
        return super().post(request, *args, **kwargs)


class GenerateAllBreaksView(UpdateAllBreaksView):

    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_GENERATE_ALL
    success_message = "Teams break generated for all break categories."

    def post(self, request, *args, **kwargs):
        BreakingTeam.objects.filter(break_category__tournament=self.get_tournament()).delete()
        return super().post(request, *args, **kwargs)


class UpdateBreakView(LogActionMixin, SingleObjectFromTournamentMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    model = BreakCategory
    slug_url_kwarg = 'category'
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ONE
    tournament_redirect_pattern_name = 'breakqual-teams'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        BreakGenerator(self.object).generate()
        messages.success(request, "Teams break updated for break category %s." % self.object.name)
        self.log_action(break_category=self.object)
        return super().post(request, *args, **kwargs)


class BaseBreakingAdjudicatorsView(TournamentMixin, VueTableTemplateView):

    page_title = 'Breaking Adjudicators'
    page_emoji = '🎉'

    def get_table(self):
        table = TabbycatTableBuilder(view=self)
        table.add_adjudicator_columns(Adjudicator.objects.filter(
            breaking=True, tournament=self.get_tournament()))
        return table


class AdminBreakingAdjudicatorsView(LoginRequiredMixin, BaseBreakingAdjudicatorsView):

    template_name = 'breaking_adjs.html'

    def get(self, request, *args, **kwargs):
        messages.info(self.request, "Adjudicators can be marked as breaking in the Feedback section.")
        return super().get(self, request, *args, **kwargs)


class PublicBreakingAdjudicatorsView(PublicTournamentPageMixin, CacheMixin, BaseBreakingAdjudicatorsView):

    public_page_preference = 'public_breaking_adjs'


class EditEligibilityFormView(LogActionMixin, SuperuserRequiredMixin, TournamentMixin, FormView):
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_ELIGIBILITY_EDIT
    form_class = forms.BreakEligibilityForm
    template_name = 'edit_eligibility.html'

    def get_success_url(self):
        return reverse_tournament('breakqual-index', self.get_tournament())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.get_tournament()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Break eligibility saved.")
        return super().form_valid(form)
