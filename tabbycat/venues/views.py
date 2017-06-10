import json

from django.contrib import messages
from django.forms import Select, SelectMultiple, TextInput
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import DrawForDragAndDropMixin, SaveDragAndDropActionMixin, TournamentMixin
from tournaments.models import Round
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import JsonDataResponsePostView, ModelFormSetView, SuperuserRequiredMixin

from .allocator import allocate_venues
from .models import Venue, VenueCategory, VenueConstraint


class VenueAllocationViewBase(DrawForDragAndDropMixin, SuperuserRequiredMixin):

    def get_unallocated_venues(self):
        unused_venues = self.get_round().unused_venues()
        return json.dumps([v.serialize() for v in unused_venues])


class EditVenuesView(VenueAllocationViewBase, TemplateView):

    template_name = "edit_venues.html"
    auto_url = "venues-auto-allocate"
    save_url = "save-debate-venues"

    def get_context_data(self, **kwargs):
        vcs = VenueConstraint.objects.all()
        kwargs['vueVenueConstraints'] = json.dumps([vc.serialize() for vc in vcs])
        kwargs['vueUnusedVenues'] = self.get_unallocated_venues()
        return super().get_context_data(**kwargs)


class AutoAllocateVenuesView(VenueAllocationViewBase, LogActionMixin, JsonDataResponsePostView):

    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE
    round_redirect_pattern_name = 'venues-edit'

    def post_data(self):
        allocate_venues(self.get_round())
        return {
            'debates': self.get_draw(),
            'unallocatedVenues': self.get_unallocated_venues()
        }

    def post(self, request, *args, **kwargs):
        round = self.get_round()
        if round.draw_status == Round.STATUS_RELEASED:
            return HttpResponseBadRequest("Draw is already released, unrelease draw to redo auto-allocations.")
        if round.draw_status != Round.STATUS_CONFIRMED:
            return HttpResponseBadRequest("Draw is not confirmed, confirm draw to run auto-allocations.")
        self.log_action()
        return super().post(request, *args, **kwargs)


class SaveVenuesView(SaveDragAndDropActionMixin):
    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_SAVE

    def get_moved_item(self, id):
        return Venue.objects.get(pk=id)

    def move_item(self, moved_to, moved_from, moved_venue, request):
        if moved_to:
            print('moving to')
            # Move to new location; update it's venue
            moved_to.venue = moved_venue
            moved_to.save()
        else:
            # Only delete old debate's venue when moving to unused; swaps done in seperate requeest
            moved_from.venue = None
            moved_from.save()
        return


class VenueCategoriesView(SuperuserRequiredMixin, TournamentMixin, ModelFormSetView):
    template_name = 'categories_edit.html'
    formset_model = VenueCategory
    formset_factory_kwargs = {
        'fields': ('name', 'description', 'display_in_venue_name',
                   'display_in_public_tooltip', 'venues'),
        'widgets': {
            'venues': SelectMultiple(attrs={'size': 10})
        },
        'extra': 3
    }

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            messages.success(self.request, _("Saved venue categories: %(list)s") % {
                'list': ", ".join(category.name for category in self.instances)
            })
        if "add_more" in self.request.POST:
            return redirect_tournament('venues-categories', self.get_tournament())
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.get_tournament())


class SelectPrepopulated(TextInput):
    template_name = 'select_prepopulated_widget.html'

    def __init__(self, data_list, *args, **kwargs):
        super(SelectPrepopulated, self).__init__(*args, **kwargs)
        self.attrs.update({'data_list': data_list})


class VenueConstraintsView(SuperuserRequiredMixin, TournamentMixin, ModelFormSetView):
    template_name = 'venue_constraints_edit.html'
    formset_model = VenueConstraint

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
            'extra': 3
        }
        return formset_factory_kwargs.copy()

    def subject_choices(self):
        from participants.models import Adjudicator, Team, Institution
        from divisions.models import Division

        tournament = self.get_tournament()
        options = []

        if tournament.pref('share_adjs'):
            adjudicators = Adjudicator.objects.filter(tournament=tournament).values_list('id', 'name').order_by('name')
        else:
            adjudicators = Adjudicator.objects.values_list('id', 'name').order_by('name')
        options.extend([(a[0], a[1] + ' (Adjudicator)') for a in adjudicators])

        teams = Team.objects.filter(tournament=tournament).values_list('id', 'short_name').order_by('short_name')
        options.extend([(t[0], t[1] + ' (Team)') for t in teams])

        institutions = Institution.objects.values_list('id', 'name').order_by('name')
        options.extend([(i[0], i[1] + ' (Institution)') for i in institutions])

        divisions = Division.objects.filter(tournament=tournament).values_list('id', 'name').order_by('name')
        options.extend([(d[0], d[1] + ' (Division)') for d in divisions])

        return sorted(options, key=lambda tup: tup[1])

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            messages.success(self.request, _("Saved %(count)d venue constraints.") % {
                'count': len(self.instances)
            })
        if "add_more" in self.request.POST:
            return redirect_tournament('venues-constraints', self.get_tournament())
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.get_tournament())
