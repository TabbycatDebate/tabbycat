from django.contrib import messages
from django.forms import SelectMultiple, TextInput
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from draw.models import Debate
from tournaments.mixins import RoundMixin, TournamentMixin
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import ModelFormSetView, PostOnlyRedirectView, SuperuserRequiredMixin

from .allocator import allocate_venues
from .models import Venue, VenueCategory, VenueConstraint


class EditVenuesView(SuperuserRequiredMixin, RoundMixin, TemplateView):

    template_name = "venues_edit.html"

    def get_context_data(self, **kwargs):
        kwargs['draw'] = self.get_round().debate_set_with_prefetches(speakers=False)
        return super().get_context_data(**kwargs)


class AutoAllocateVenuesView(LogActionMixin, SuperuserRequiredMixin, RoundMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE
    round_redirect_pattern_name = 'venues-edit'

    def post(self, request, *args, **kwargs):
        allocate_venues(self.get_round())
        self.log_action()
        return super().post(request, *args, **kwargs)


class SaveVenuesView(LogActionMixin, SuperuserRequiredMixin, RoundMixin, View):

    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_SAVE

    def post(self, request, *args, **kwargs):

        def v_id(a):
            try:
                return int(request.POST[a].split('_')[1])
            except IndexError:
                return None

        data = [(int(a.split('_')[1]), v_id(a)) for a in list(request.POST.keys())]

        debates = Debate.objects.in_bulk([d_id for d_id, _ in data])
        venues = Venue.objects.in_bulk([v_id for _, v_id in data])
        for debate_id, venue_id in data:
            debates[debate_id].venue = venues[venue_id] if venue_id is not None else None
            debates[debate_id].save()

        self.log_action()
        return HttpResponse("ok")


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
                'subject_id': 'Start typing the name of the person/team/institution you want to constrain'
            },
            'widgets': {
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

        adjudicators = Adjudicator.objects.filter(tournament=tournament).values_list('id', 'name').order_by('name')
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
