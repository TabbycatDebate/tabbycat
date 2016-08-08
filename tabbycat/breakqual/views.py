from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from utils.misc import reverse_tournament
from utils.mixins import (CacheMixin, PostOnlyRedirectView, SingleObjectFromTournamentMixin,
                          SuperuserRequiredMixin, VueTableTemplateView)
from utils.tables import TabbycatTableBuilder
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .utils import get_breaking_teams
from .generator import BreakGenerator
from .models import BreakCategory, BreakingTeam
from . import forms


class PublicBreakIndexView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'public_results'
    template_name = 'public_break_index.html'


class AdminBreakIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = 'breaking_index.html'


class BaseBreakingTeamsView(SingleObjectFromTournamentMixin, VueTableTemplateView):

    model = BreakCategory
    slug_url_kwarg = 'category'
    page_emoji = '👑'

    def get_standings(self):
        return get_breaking_teams(self.object, prefetch=('speaker_set',))

    def get_table(self):
        self.standings = self.get_standings()
        table = TabbycatTableBuilder(view=self, title=self.object.name)
        table.add_ranking_columns(self.standings)
        table.add_column("Break", [tsi.break_rank for tsi in self.standings])
        table.add_team_columns([tsi.team for tsi in self.standings])
        table.add_metric_columns(self.standings)
        return table

    def get_page_title(self):
        return self.object.name + " Break"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class PublicBreakingTeamsView(PublicTournamentPageMixin, CacheMixin, BaseBreakingTeamsView):
    public_page_preference = 'public_breaking_teams'


class BreakingTeamsFormView(LogActionMixin, SuperuserRequiredMixin, BaseBreakingTeamsView, FormView):
    # inherit from two views, not best practice but works in this scenario

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

        # Populate the form here, so we can save it in self.form
        self.form = self.get_form()
        kwargs['form'] = self.form

        return super().get_context_data(**kwargs)

    def get_standings(self):
        return get_breaking_teams(self.object, prefetch=('speaker_set', 'break_categories'),
                rankings=BreakGenerator(self.object).rankings)

    def get_table(self):
        table = super().get_table()  # as for public view, but add some more columns
        table.add_column("Eligible for", [", ".join(bc.name for bc in tsi.team.break_categories.all()) for tsi in self.standings])
        table.add_column("Edit Remark", [str(self.form.get_remark_field(tsi.team)) for tsi in self.standings])
        return table

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
        table.add_adjudicator_columns(self.get_tournament().adjudicator_set.filter(breaking=True))
        return table


class AdminBreakingAdjudicatorsView(LoginRequiredMixin, BaseBreakingAdjudicatorsView):
    template_name = 'breaking_adjs.html'


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
