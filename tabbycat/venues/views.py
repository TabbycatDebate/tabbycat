import logging

from django.contrib import messages
from django.db.models import Max, Min, Q
from django.forms import Select
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from availability.utils import annotate_availability
from tournaments.mixins import DebateDragAndDropMixin, TournamentMixin
from utils.forms import SelectPrepopulated
from utils.misc import ranks_dictionary, redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import ModelFormSetView

from .forms import venuecategoryform_factory
from .models import Venue, VenueCategory, VenueConstraint
from .serializers import EditDebateVenuesDebateSerializer, EditDebateVenuesVenueSerializer

logger = logging.getLogger(__name__)


class EditDebateVenuesView(DebateDragAndDropMixin, AdministratorMixin, TemplateView):
    template_name = "edit_debate_venues.html"
    page_title = gettext_lazy("Edit Rooms")
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
        p_range = Venue.objects.filter(tournament=self.tournament).aggregate(
            min=Min('priority'), max=Max('priority'))
        info = super().get_extra_info()
        info['highlights']['priority'] = ranks_dictionary(
            self.tournament, p_range['min'], p_range['max'])
        # Most recently created venues take priority in getting the highlight
        vcs = VenueCategory.objects.order_by('id').reverse()
        info['highlights']['category'] = [{'pk': vc.id, 'fields': {'name': vc.name}} for vc in vcs]
        return info


class VenueCategoriesView(LogActionMixin, AdministratorMixin, TournamentMixin, ModelFormSetView):
    template_name = 'venue_categories_edit.html'
    formset_model = VenueCategory
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CATEGORIES_EDIT

    def get_formset_factory_kwargs(self):
        queryset = self.tournament.relevant_venues.prefetch_related('venuecategory_set')
        formset_factory_kwargs = {
            'form': venuecategoryform_factory(venues_queryset=queryset),
            'extra': 3,
        }
        return formset_factory_kwargs

    def get_formset(self):
        formset = super().get_formset()
        # Show relevant venues; not all venues
        venues = self.tournament.relevant_venues.all()
        for form in formset:
            form.fields['venues'].queryset = venues
        return formset

    def get_formset_queryset(self):
        return self.tournament.venuecategory_set.all()

    def formset_valid(self, formset):
        self.instances = formset.save(commit=False)
        if self.instances:
            for category in self.instances:
                category.tournament = self.tournament

            message = ngettext("Saved room category: %(list)s",
                "Saved venue categories: %(list)s",
                len(self.instances),
            ) % {'list': ", ".join(category.name for category in self.instances)}
            messages.success(self.request, message)
        else:
            messages.success(self.request, _("No changes were made to the room categories."))

        if "add_more" in self.request.POST:
            return redirect_tournament('venues-categories', self.tournament)
        return super().formset_valid(formset)

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.tournament)


class VenueConstraintsView(AdministratorMixin, LogActionMixin, TournamentMixin, ModelFormSetView):
    template_name = 'venue_constraints_edit.html'
    formset_model = VenueConstraint
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUE_CONSTRAINTS_EDIT

    def get_formset_factory_kwargs(self):
        # Need to built a dynamic choices list for the widget; so override the
        # standard method of getting args
        formset_factory_kwargs = {
            'fields': ('subject_content_type', 'subject_id', 'category', 'priority'),
            'labels': {
                'subject_content_type': 'Constrainee Type',
                'subject_id': 'Constrainee ID',
                'category': 'Room Category',
            },
            'help_texts': {
                'subject_id': 'Delete the existing number and start typing the name of the person/team/institution you want to constrain to lookup their ID.',
            },
            'widgets': {
                'subject_content_type': Select(attrs={'data-filter': True}),
                'subject_id': SelectPrepopulated(data_list=self.subject_choices()),
            },
            'extra': 8,
        }
        return formset_factory_kwargs

    def get_formset_queryset(self):
        # Show relevant venue constraints; not all venue constraints
        q = Q(adjudicator__isnull=False, adjudicator__tournament=self.tournament)
        q |= Q(team__isnull=False, team__tournament=self.tournament)
        q |= Q(institution__isnull=False)

        return VenueConstraint.objects.filter(q)

    def subject_choices(self):
        from participants.models import Institution

        options = []

        adjudicators = self.tournament.relevant_adjudicators.values('id', 'name')
        options.extend([(a['id'], _('%s (Adjudicator)') % a['name']) for a in adjudicators])

        teams = self.tournament.team_set.values('id', 'short_name')
        options.extend([(t['id'], _('%s (Team)') % t['short_name']) for t in teams])

        institutions = Institution.objects.values('id', 'name')
        options.extend([(i['id'], _('%s (Institution)') % i['name']) for i in institutions])

        return sorted(options, key=lambda x: x[1])

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            count = len(self.instances)
            message = ngettext("Saved %(count)d room constraint.",
                "Saved %(count)d room constraints.", count) % {'count': count}
            messages.success(self.request, message)
        if "add_more" in self.request.POST:
            return redirect_tournament('venues-constraints', self.tournament)
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.tournament)
