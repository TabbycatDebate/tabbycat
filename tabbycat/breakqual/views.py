import json
import logging

from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView, View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from participants.models import Team
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, CacheMixin
from utils.views import PostOnlyRedirectView, VueTableTemplateView
from utils.tables import TabbycatTableBuilder
from tournaments.mixins import PublicTournamentPageMixin, SingleObjectFromTournamentMixin, TournamentMixin

from .base import BreakGeneratorError
from .utils import breakcategories_with_counts, get_breaking_teams
from .generator import BreakGenerator
from .models import BreakCategory, BreakingTeam
from . import forms

logger = logging.getLogger(__name__)


class PublicBreakIndexView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'public_results'
    template_name = 'public_break_index.html'


class AdminBreakIndexView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = 'breaking_index.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['categories'] = breakcategories_with_counts(tournament)
        kwargs['no_teams_eligible'] = not BreakCategory.team_set.through.objects.filter(breakcategory__tournament=tournament).exists()
        kwargs['break_not_generated'] = not BreakingTeam.objects.filter(break_category__tournament=tournament).exists()
        return super().get_context_data(**kwargs)


# ==============================================================================
# Teams
# ==============================================================================

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
        table.add_column({'title': _("Break"), 'key': 'break'},
                         [tsi.break_rank for tsi in self.standings])
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


class BreakingTeamsFormView(GenerateBreakMixin, LogActionMixin, AdministratorMixin, BaseBreakingTeamsView, FormView):
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
        table.add_column(_("Eligible for"), [", ".join(bc.name for bc in tsi.team.break_categories.all()) for tsi in self.standings])
        table.add_column(_("Edit Remark"), [str(self.form.get_remark_field(tsi.team)) for tsi in self.standings])
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
            messages.success(self.request, _("Changes to breaking team remarks saved."))

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class GenerateAllBreaksView(GenerateBreakMixin, LogActionMixin, TournamentMixin, AdministratorMixin, PostOnlyRedirectView):

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


# ==============================================================================
# Adjudicators
# ==============================================================================

class BaseBreakingAdjudicatorsView(TournamentMixin, VueTableTemplateView):

    page_title = _("Breaking Adjudicators")
    page_emoji = '🎉'

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key='name')
        table.add_adjudicator_columns(self.get_tournament().adjudicator_set.filter(breaking=True))
        return table


class AdminBreakingAdjudicatorsView(AdministratorMixin, BaseBreakingAdjudicatorsView):
    template_name = 'breaking_adjs.html'


class PublicBreakingAdjudicatorsView(PublicTournamentPageMixin, CacheMixin, BaseBreakingAdjudicatorsView):
    public_page_preference = 'public_breaking_adjs'


# ==============================================================================
# Eligibility and categories
# ==============================================================================

class EditTeamEligibilityView(AdministratorMixin, TournamentMixin, VueTableTemplateView):

    template_name = 'edit_break_eligibility.html'
    page_title = _("Break Eligibility")
    page_emoji = '🍯'

    def get_table(self):
        t = self.get_tournament()
        table = TabbycatTableBuilder(view=self, sort_key='team')
        teams = t.team_set.all().select_related(
            'institution').prefetch_related('break_categories', 'speaker_set')
        table.add_team_columns(teams)
        break_categories = t.breakcategory_set.all()

        for bc in break_categories:
            table.add_column({'title': bc.name, 'key': bc.name}, [{
                'component': 'check-cell',
                'checked': True if bc in team.break_categories.all() else False,
                'id': team.id,
                'type': bc.id
            } for team in teams])
        return table

    def get_context_data(self, **kwargs):
        break_categories = self.get_tournament().breakcategory_set.all()
        json_categories = [bc.serialize for bc in break_categories]
        kwargs["break_categories"] = json.dumps(json_categories)
        kwargs["break_categories_length"] = break_categories.count()
        return super().get_context_data(**kwargs)


class UpdateEligibilityEditView(LogActionMixin, AdministratorMixin, TournamentMixin, View):
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_ELIGIBILITY_EDIT

    def set_break_elibility(self, team, sent_status):
        category_id = sent_status['type']
        marked_eligible = team.break_categories.filter(pk=category_id).exists()
        if sent_status['checked'] and not marked_eligible:
            team.break_categories.add(category_id)
            team.save()
        elif not sent_status['checked'] and marked_eligible:
            team.break_categories.remove(category_id)
            team.save()

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)

        try:
            team_ids = [int(key) for key in posted_info.keys()]
            teams = Team.objects.prefetch_related('break_categories').in_bulk(team_ids)
            for team_id, team in teams.items():
                self.set_break_elibility(team, posted_info[str(team_id)])
            self.log_action()
        except:
            message = "Error handling eligiblity updates"
            logger.exception(message)
            return JsonResponse({'status': 'false', 'message': message}, status=500)

        return JsonResponse(json.dumps(True), safe=False)
