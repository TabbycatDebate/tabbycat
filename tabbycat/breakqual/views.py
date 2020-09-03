import json
import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.forms import HiddenInput
from django.forms.models import BaseModelFormSet
from django.utils.translation import gettext as _, ngettext
from django.views.generic import FormView, TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from participants.models import Team
from participants.views import EditSpeakerCategoriesView, UpdateEligibilityEditView as BaseUpdateEligibilityEditView
from tournaments.mixins import PublicTournamentPageMixin, SingleObjectFromTournamentMixin, TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import PostOnlyRedirectView, VueTableTemplateView

from . import forms
from .base import BreakGeneratorError
from .generator import BreakGenerator
from .models import BreakCategory, BreakingTeam
from .serializers import BreakCategorySerializer
from .utils import auto_make_break_rounds, breakcategories_with_counts, get_breaking_teams

logger = logging.getLogger(__name__)


class PublicBreakIndexView(PublicTournamentPageMixin, TemplateView):
    public_page_preference = 'public_results'
    template_name = 'public_break_index.html'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


class AdminBreakIndexView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = 'breaking_index.html'

    def get_context_data(self, **kwargs):
        tournament = self.tournament
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
        return _("%(category)s Break") % {'category': self.object.name}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class PublicBreakingTeamsView(PublicTournamentPageMixin, BaseBreakingTeamsView):
    public_page_preference = 'public_breaking_teams'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


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
        return reverse_tournament('breakqual-teams', self.tournament, kwargs={'category': self.object.slug})

    def get_context_data(self, **kwargs):
        kwargs['generated'] = BreakingTeam.objects.filter(
                break_category__tournament=self.tournament).exists()
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
        table.add_column(
            {'key': 'eligible-for', 'title': _("Eligible for")},
            [", ".join(bc.name for bc in tsi.team.break_categories.all()) for tsi in self.standings],
        )
        table.add_column(
            {'key': 'edit-remark', 'title': _("Edit Remark")},
            [str(self.form.get_remark_field(tsi.team)) for tsi in self.standings],
        )
        return table

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.object
        return kwargs

    def form_valid(self, form):
        form.save()

        if 'save_update_all' in self.request.POST:
            successes = self.generate_break(self.tournament.breakcategory_set.order_by('-priority'))
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
        BreakingTeam.objects.filter(break_category__tournament=self.tournament).delete()
        tournament = self.tournament

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
        table.add_adjudicator_columns(self.tournament.adjudicator_set.filter(breaking=True))
        return table


class AdminBreakingAdjudicatorsView(AdministratorMixin, BaseBreakingAdjudicatorsView):
    template_name = 'breaking_adjs.html'


class PublicBreakingAdjudicatorsView(PublicTournamentPageMixin, BaseBreakingAdjudicatorsView):
    public_page_preference = 'public_breaking_adjs'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


# ==============================================================================
# Eligibility and categories
# ==============================================================================


class BreakCategoryModelFormSet(BaseModelFormSet):
    """Class to handle the different procedures for creation and modification
    in BreakCategory objects."""

    def save_new(self, form, commit=True):
        """Create break rounds for new break categories"""
        bc = super().save_new(form, commit)
        auto_make_break_rounds(bc, prefix=True)
        return bc

    def save_existing(self, form, instance, commit=True):
        """Stub for deleting/creating break rounds if break size changes"""
        return super().save_existing(form, instance, commit)


class EditBreakCategoriesView(EditSpeakerCategoriesView):
    # The tournament is included in the form as a hidden input so that
    # uniqueness checks will work. Since this is a superuser form, they can
    # access all tournaments anyway, so tournament forgery wouldn't be a
    # security risk.

    template_name = 'break_categories_edit.html'
    formset_model = BreakCategory
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_CATEGORIES_EDIT

    url_name = 'break-categories-edit'
    success_url = 'breakqual-index'

    def get_formset_factory_kwargs(self):
        return {
            'fields': ('name', 'tournament', 'slug', 'seq', 'break_size', 'is_general', 'priority', 'limit'),
            'extra': 2,
            'widgets': {
                'tournament': HiddenInput,
            },
            'formset': BreakCategoryModelFormSet,
        }


class EditTeamEligibilityView(AdministratorMixin, TournamentMixin, VueTableTemplateView):

    template_name = 'edit_break_eligibility.html'
    page_title = _("Break Eligibility")
    page_emoji = '🍯'

    def get_table(self):
        t = self.tournament
        table = TabbycatTableBuilder(view=self, sort_key='team')
        teams = t.team_set.all().select_related(
            'institution').prefetch_related('break_categories', 'speaker_set')
        speaker_categories = t.speakercategory_set.order_by('seq')

        nspeaker_annotations = {}
        for sc in speaker_categories:
            nspeaker_annotations['nspeakers_%s' % sc.slug] = Count(
                'speaker', filter=Q(speaker__categories=sc))
        teams = teams.annotate(**nspeaker_annotations)

        table.add_team_columns(teams)

        break_categories = t.breakcategory_set.order_by('seq')
        for bc in break_categories:
            table.add_column({'title': bc.name, 'key': bc.slug}, [{
                'component': 'check-cell',
                'checked': True if bc in team.break_categories.all() else False,
                'sort': True if bc in team.break_categories.all() else False,
                'id': team.id,
                'type': bc.id,
            } for team in teams])

        # Provide list of members within speaker categories for convenient entry
        for sc in speaker_categories:
            table.add_column({'title': _('%s Speakers') % sc.name, 'key': sc.name + "_speakers"}, [{
                'text': getattr(team, 'nspeakers_%s' % sc.slug, 'N/A'),
                'tooltip': ngettext(
                    'Team has %(nspeakers)s speaker with the %(category)s speaker category assigned',
                    'Team has %(nspeakers)s speakers with the %(category)s speaker category assigned',
                    getattr(team, 'nspeakers_%s' % sc.slug, 0),
                ) % {'nspeakers': getattr(team, 'nspeakers_%s' % sc.slug, 'N/A'), 'category': sc.name},
            } for team in teams])

        return table

    def get_context_data(self, **kwargs):
        break_categories = self.tournament.breakcategory_set.all()
        json_categories = BreakCategorySerializer(break_categories, many=True).data
        kwargs["break_categories"] = json.dumps(json_categories)
        kwargs["break_categories_length"] = break_categories.count()
        return super().get_context_data(**kwargs)


class UpdateEligibilityEditView(BaseUpdateEligibilityEditView):
    action_log_type = ActionLogEntry.ACTION_TYPE_BREAK_ELIGIBILITY_EDIT
    participant_model = Team
    many_to_many_field = 'break_categories'
