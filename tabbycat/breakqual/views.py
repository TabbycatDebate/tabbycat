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

from .breaking import get_breaking_teams
from .generator import BreakGenerator
from .models import BreakCategory, BreakingTeam
from . import forms


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

        standings = get_breaking_teams(self.object, include_categories=t.pref('public_break_categories'))

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
    model = BreakCategory
    slug_url_kwarg = 'category'
    form_class = forms.BreakingTeamsForm
    template_name = 'breaking_teams.html'

    def get_action_log_type(self):
        if 'save_update_all' in self.request.POST:
            return ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ALL
        elif 'save_update_one' in self.request.POST:
            return ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ONE
        else:
            return ActionLogEntry.ACTION_TYPE_BREAK_EDIT_REMARKS

    def get_action_log_fields(self, **kwargs):
        kwargs['break_category'] = self.object
        return super().get_action_log_fields(**kwargs)

    def get_success_url(self):
        return reverse_tournament('breakqual-teams', self.get_tournament(), kwargs={'category': self.object.slug})

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

        if 'save_update_all' in self.request.POST:
            for category in self.get_tournament().breakcategory_set.order_by('-priority'):
                BreakGenerator(category).generate()
            messages.success(self.request, "Changes to breaking team remarks saved "
                    "and teams break updated for all break categories.")
        elif 'save_update_one' in self.request.POST:
            BreakGenerator(self.object).generate()
            messages.success(self.request, "Changes to breaking team remarks saved "
                    "and teams break updated for break category %s." % self.object.name)
        else:
            messages.success(self.request, "Changes to breaking team remarks saved.")

        self.log_action()
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class GenerateAllBreaksView(LogActionMixin, TournamentMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_GENERATE_ALL
    tournament_redirect_pattern_name = 'breakqual-teams'

    def post(self, request, *args, **kwargs):
        BreakingTeam.objects.filter(break_category__tournament=self.get_tournament()).delete()
        tournament = self.get_tournament()
        for category in tournament.breakcategory_set.order_by('-priority'):
            BreakGenerator(category).generate()
        messages.success(request, "Teams break generated for all break categories.")
        self.log_action()
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
