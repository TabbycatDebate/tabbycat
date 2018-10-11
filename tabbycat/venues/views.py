import json
import logging

from django.contrib import messages
from django.db.models import Q
from django.forms import Select
from django.utils.translation import ngettext
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import DrawForDragAndDropMixin, TournamentMixin
from tournaments.models import Round
from tournaments.views import BaseSaveDragAndDropDebateJsonView
from utils.forms import SelectPrepopulated
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView, ModelFormSetView

from .allocator import allocate_venues
from .forms import venuecategoryform_factory
from .models import Venue, VenueCategory, VenueConstraint

logger = logging.getLogger(__name__)


class EditDebateVenuesView(AdministratorMixin, TemplateView):
    template_name = "edit_debate_venues.html"


class LegacyVenueAllocationMixin(DrawForDragAndDropMixin, AdministratorMixin):

    def get_unallocated_venues(self):
        unused_venues = self.round.unused_venues().prefetch_related('venuecategory_set')
        return json.dumps([v.serialize() for v in unused_venues])


class LegacyEditVenuesView(LegacyVenueAllocationMixin, TemplateView):

    template_name = "legacy_edit_venues.html"
    auto_url = "legacy-venues-auto-allocate"
    save_url = "legacy-save-debate-venues"

    def get_context_data(self, **kwargs):
        vcs = VenueConstraint.objects.prefetch_related('subject')
        kwargs['vueVenueConstraints'] = json.dumps([vc.serialize() for vc in vcs])
        kwargs['vueUnusedVenues'] = self.get_unallocated_venues()
        return super().get_context_data(**kwargs)


class LegacyAutoAllocateVenuesView(LegacyVenueAllocationMixin, LogActionMixin, JsonDataResponsePostView):

    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE
    round_redirect_pattern_name = 'legacy-venues-edit'

    def post_data(self):
        self.log_action()
        if self.round.draw_status == Round.STATUS_RELEASED:
            info = "Draw is already released, unrelease draw to redo auto-allocations."
            logger.warning(info)
            raise BadJsonRequestError(info)
        if self.round.draw_status != Round.STATUS_CONFIRMED:
            info = "Draw is not confirmed, confirm draw to run auto-allocations."
            logger.warning(info)
            raise BadJsonRequestError(info)

        allocate_venues(self.round)
        return {
            'debates': self.get_draw(),
            'unallocatedVenues': self.get_unallocated_venues()
        }


class LegacySaveVenuesView(BaseSaveDragAndDropDebateJsonView):
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_SAVE

    def get_moved_item(self, id):
        return Venue.objects.get(pk=id)

    def modify_debate(self, debate, posted_debate):
        if posted_debate['venue']:
            debate.venue = Venue.objects.get(pk=posted_debate['venue']['id'])
        else:
            debate.venue = None
        debate.save()
        return debate


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
                'category': 'Venue Category'
            },
            'help_texts': {
                'subject_id': 'Delete the existing number and start typing the name of the person/team/institution you want to constrain to lookup their ID.'
            },
            'widgets': {
                'subject_content_type': Select(attrs={'data-filter': True}),
                'subject_id': SelectPrepopulated(data_list=self.subject_choices())
            },
            'extra': 8
        }
        return formset_factory_kwargs

    def get_formset_queryset(self):
        # Show relevant venue constraints; not all venue constraints
        q = Q(adjudicator__isnull=False, adjudicator__tournament=self.tournament)
        q |= Q(team__isnull=False, team__tournament=self.tournament)
        q |= Q(division__isnull=False, division__tournament=self.tournament)
        q |= Q(institution__isnull=False)
        if self.tournament.pref('share_adjs'):
            q |= Q(adjudicator__isnull=False, adjudicator__tournament__isnull=True)

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

        divisions = self.tournament.division_set.values('id', 'name')
        options.extend([(d['id'], _('%s (Division)') % d['name']) for d in divisions])

        return sorted(options, key=lambda x: x[1])

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            count = len(self.instances)
            message = ngettext("Saved %(count)d venue constraint.",
                "Saved %(count)d venue constraints.", count) % {'count': count}
            messages.success(self.request, message)
        if "add_more" in self.request.POST:
            return redirect_tournament('venues-constraints', self.tournament)
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.tournament)
