from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from utils.misc import reverse_tournament
from utils.mixins import CacheMixin, PostOnlyRedirectView, SuperuserRequiredMixin, VueTableTemplateView
from utils.tables import TabbycatTableBuilder
from tournaments.mixins import PublicTournamentPageMixin, SingleObjectFromTournamentMixin, TournamentMixin

from .base import BreakGeneratorError
from .utils import breakcategories_with_counts, get_breaking_teams
from .generator import BreakGenerator
from .models import BreakCategory, BreakingTeam
from . import forms


class PublicBreakIndexView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'public_results'
    template_name = 'public_break_index.html'


class AdminBreakIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = 'breaking_index.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['categories'] = breakcategories_with_counts(tournament)
        kwargs['no_teams_eligible'] = not BreakCategory.team_set.through.objects.filter(breakcategory__tournament=tournament).exists()
        kwargs['break_not_generated'] = not BreakingTeam.objects.filter(break_category__tournament=tournament).exists()
        return super().get_context_data(**kwargs)


class BaseBreakingTeamsView(SingleObjectFromTournamentMixin, VueTableTemplateView):

    model = BreakCategory
    slug_url_kwarg = 'category'
    page_emoji = '👑'

    def get_standings(self):
        return get_breaking_teams(self.object, prefetch=('speaker_set',))

    def get_table(self):
        self.standings = self.get_standings()
        table = TabbycatTableBuilder(view=self, title=self.object.name, sort_key='Rk')
        table.add_ranking_columns(self.standings)
        table.add_column("Break", [tsi.break_rank for tsi in self.standings])
        table.add_team_columns([tsi.team for tsi in self.standings])
        table.add_metric_columns(self.standings)
        return table

    def get_page_title(self):
        return _("%(category)s Break") % {'category': self.object.name,}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class PublicBreakingTeamsView(PublicTournamentPageMixin, CacheMixin, BaseBreakingTeamsView):
    public_page_preference = 'public_breaking_teams'


class GenerateBreakMixin:

    def generate_break(self, categories):
        """Generates the break for the given categories. Adds a messages error
        for each category where break generation failed; returns a string
        containing a list of names of categories where breaks were successfully
        generated."""
        successes = []
        for category in categories:
            try:
                BreakGenerator(category).generate()
            except BreakGeneratorError as e:
                messages.error(self.request, _("There was an error generating the break for category "
                    "%(category)s: %(message)s") % {'category': category.name, 'message': str(e)})
            else:
                successes.append(category.name)
        return ", ".join(successes)


class BreakingTeamsFormView(GenerateBreakMixin, LogActionMixin, SuperuserRequiredMixin, BaseBreakingTeamsView, FormView):
    # inherit from two views, not best practice but works in this scenario

    form_class = forms.BreakingTeamsForm
    template_name = 'breaking_teams.html'
    action_log_content_object_attr = 'object'

    def get_action_log_type(self):
        if 'save_update_all' in self.request.POST:
            return ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ALL
        elif 'save_update_one' in self.request.POST:
            return ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ONE
        else:
            return ActionLogEntry.ACTION_TYPE_BREAK_EDIT_REMARKS

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
            successes = self.generate_break(self.get_tournament().breakcategory_set.order_by('-priority'))
            if successes:
                messages.success(self.request, _("Changes to breaking team remarks saved "
                        "and teams break updated for the following break categories: "
                        "%(categories)s.") % {'categories': successes})

        elif 'save_update_one' in self.request.POST:
            successes = self.generate_break([self.object])
            if successes:
                messages.success(self.request, _("Changes to breaking team remarks saved "
                        "and teams break updated for break category %(category)s.") %
                        {'category': self.object.name})

        else:
            messages.success(self.request, "Changes to breaking team remarks saved.")

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class GenerateAllBreaksView(GenerateBreakMixin, LogActionMixin, TournamentMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_GENERATE_ALL
    tournament_redirect_pattern_name = 'breakqual-teams'

    def post(self, request, *args, **kwargs):
        BreakingTeam.objects.filter(break_category__tournament=self.get_tournament()).delete()
        tournament = self.get_tournament()

        successes = self.generate_break(tournament.breakcategory_set.order_by('-priority'))
        if successes:
            messages.success(request, _("Teams break generated for the following break categories: "
                "%(categories)s.") % {'categories': successes})

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
