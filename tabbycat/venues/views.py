import logging

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import Select
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.views import BaseConstraintsView
from availability.utils import annotate_availability
from participants.models import Adjudicator, Institution, Team
from tournaments.mixins import DebateDragAndDropMixin, TournamentMixin
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import ModelFormSetView

from .forms import venuecategoryform_factory
from .models import Venue, VenueCategory, VenueConstraint
from .serializers import EditDebateVenuesDebateSerializer, EditDebateVenuesVenueSerializer

logger = logging.getLogger(__name__)


class EditDebateVenuesView(DebateDragAndDropMixin, AdministratorMixin, TemplateView):
    template_name = "edit_debate_venues.html"
    page_title = gettext_lazy("Edit Venues")
    prefetch_venues = False # Fetched in full as get_serialised

    def debates_or_panels_factory(self, debates):
        return EditDebateVenuesDebateSerializer(
            debates, many=True, context={'sides': self.tournament.sides})

    def get_serialised_allocatable_items(self):
        venues = Venue.objects.filter(tournament=self.tournament).prefetch_related('venuecategory_set')
        venues = annotate_availability(venues, self.round)
        serialized_venues = EditDebateVenuesVenueSerializer(venues, many=True)
        return self.json_render(serialized_venues.data)

    def get_extra_info(self):
        info = super().get_extra_info()
        info['highlights']['priority'] = [] # TODO - venue priority range
        info['highlights']['category'] = [] # TODO - venue category
        info['highlights']['break'] = [] # TODO

        allocation_preferences = [
            'draw_rules__venue_allocation_method',
            'draw_rules__venue_history_cost',
            'draw_rules__venue_constraint_cost',
            'draw_rules__venue_score_cost'
        ]
        info['allocationSettings'] = {}
        for key in allocation_preferences:
            info['allocationSettings'][key] = self.tournament.preferences[key]

        return info


class VenueCategoriesView(LogActionMixin, AdministratorMixin, TournamentMixin, ModelFormSetView):
    template_name = 'venue_categories_edit.html'
    formset_model = VenueCategory
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CATEGORIES_EDIT

    def get_formset_factory_kwargs(self):
        queryset = self.tournament.relevant_venues.prefetch_related('venuecategory_set')
        formset_factory_kwargs = {
            'form': venuecategoryform_factory(venues_queryset=queryset),
            'extra': 3
        }
        return formset_factory_kwargs

    def get_formset(self):
        formset = super().get_formset()
        # Show relevant venues; not all venues
        venues = self.tournament.relevant_venues.all()
        for form in formset:
            form.fields['venues'].queryset = venues
        return formset

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            message = ngettext("Saved venue category: %(list)s",
                "Saved venue categories: %(list)s",
                len(self.instances)
            ) % {'list': ", ".join(category.name for category in self.instances)}
            messages.success(self.request, message)
        else:
            messages.success(self.request, _("No changes were made to the venue categories."))
        if "add_more" in self.request.POST:
            return redirect_tournament('venues-categories', self.tournament)
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.tournament)


# ==============================================================================
# Constraint formset views
# ==============================================================================

class BaseVenueConstraintsView(BaseConstraintsView):
    formset_model = VenueConstraint
    page_emoji = '🏰'
    template_name = 'venue_constraints_edit.html'

    def get_formset_factory_kwargs(self):
        subject_choices = [(None, '---------')] + list(self.get_subject_queryset())
        factory_kwargs = super().get_formset_factory_kwargs()
        factory_kwargs.update({
            'fields': ['category', 'subject_id', 'priority'],
            'labels': {'category': _("Venue Category"), 'subject_id': self.subject},
            'widgets': {'subject_id': Select(choices=subject_choices)}
        })
        return factory_kwargs

    def formset_valid(self, formset):
        self.instances = formset.save(commit=False)
        for c in self.instances:
            c.subject_content_type = self.contenttype
            c.save()

        for c in formset.deleted_objects:
            c.delete()

        return super().formset_valid(formset)

    def add_message(self, nsaved, ndeleted):
        if nsaved > 0:
            messages.success(self.request, self.get_save_message(nsaved))
        if ndeleted > 0:
            messages.success(self.request, self.get_delete_message(ndeleted))
        if nsaved == 0 and ndeleted == 0:
            messages.success(self.request, self.unchanged_message)

    def get_save_message(self, nsaved):
        raise NotImplementedError

    def get_delete_message(self, ndeleted):
        raise NotImplementedError


class VenueTeamConstraintsView(BaseVenueConstraintsView):
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CONSTRAINTS_TEAM_EDIT
    page_title = gettext_lazy("Venue-Team Constraints")
    save_text = gettext_lazy("Save Venue-Team Constraints")
    same_view = 'venues-constraints-team'

    subject = gettext_lazy("Team")
    unchanged_message = gettext_lazy("No changes were made to venue-team constraints.")

    contenttype = ContentType.objects.get_for_model(Team)

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(team__tournament=self.tournament)

    def get_subject_queryset(self):
        return self.tournament.team_set.order_by('short_name').values_list('id', 'short_name')

    def get_save_message(self, nsaved):
        return ngettext(
            "Saved %(count)d venue-team constraint.",
            "Saved %(count)d venue-team constraints.",
            nsaved,
        ) % {'count': nsaved}

    def get_delete_message(self, ndeleted):
        return ngettext(
            "Deleted %(count)d venue-team constraint.",
            "Deleted %(count)d venue-team constraints.",
            ndeleted,
        ) % {'count': ndeleted}


class VenueAdjudicatorConstraintsView(BaseVenueConstraintsView):
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CONSTRAINTS_ADJ_EDIT
    page_title = gettext_lazy("Venue-Adjudicator Constraints")
    save_text = gettext_lazy("Save Venue-Adjudicator Constraints")
    same_view = 'venues-constraints-adjudicator'

    subject = gettext_lazy("Adjudicator")
    unchanged_message = gettext_lazy("No changes were made to venue-adjudicator constraints.")

    contenttype = ContentType.objects.get_for_model(Adjudicator)

    def get_formset_queryset(self):
        q = Q(adjudicator__tournament=self.tournament)
        if self.tournament.pref('share_adjs'):
            q |= Q(adjudicator__tournament__isnull=True)

        return self.formset_model.objects.filter(q)

    def get_subject_queryset(self):
        return self.tournament.relevant_adjudicators.order_by('name').values_list('id', 'name')

    def get_save_message(self, nsaved):
        return ngettext(
            "Saved %(count)d venue-adjudicator constraint.",
            "Saved %(count)d venue-adjudicator constraints.",
            nsaved,
        ) % {'count': nsaved}

    def get_delete_message(self, ndeleted):
        return ngettext(
            "Deleted %(count)d venue-adjudicator constraint.",
            "Deleted %(count)d venue-adjudicator constraints.",
            ndeleted,
        ) % {'count': ndeleted}


class VenueInstitutionConstraintsView(BaseVenueConstraintsView):
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CONSTRAINTS_INST_EDIT
    page_title = gettext_lazy("Venue-Institution Constraints")
    save_text = gettext_lazy("Save Venue-Institution Constraints")
    same_view = 'venues-constraints-institution'

    subject = gettext_lazy("Institution")
    unchanged_message = gettext_lazy("No changes were made to venue-institution constraints.")

    contenttype = ContentType.objects.get_for_model(Institution)

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(institution__team__tournament=self.tournament).distinct()

    def get_subject_queryset(self):
        return Institution.objects.filter(
            team__tournament=self.tournament
        ).distinct().order_by('name').values_list('id', 'name')

    def get_save_message(self, nsaved):
        return ngettext(
            "Saved %(count)d venue-institution constraint.",
            "Saved %(count)d venue-institution constraints.",
            nsaved,
        ) % {'count': nsaved}

    def get_delete_message(self, ndeleted):
        return ngettext(
            "Deleted %(count)d venue-institution constraint.",
            "Deleted %(count)d venue-institution constraints.",
            ndeleted,
        ) % {'count': ndeleted}
