from django.contrib import messages
from django.forms import SelectMultiple
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
from .models import Venue, VenueCategory


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
        return reverse_tournament('importer-visual-index', self.get_tournament())
