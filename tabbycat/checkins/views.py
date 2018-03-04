from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _

from participants.models import Speaker
from utils.mixins import AdministratorMixin, AssistantMixin
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import Event, PersonIdentifier, VenueIdentifier


class CheckInScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'
    page_title = _('Scan Identifiers')
    page_emoji = '🎹'


class AdminCheckInScanView(AdministratorMixin, CheckInScanView):
    pass


class AssistantCheckInScanView(AssistantMixin, CheckInScanView):
    pass


class CheckInStatusView(TournamentMixin, TemplateView):
    template_name = 'checkin_status.html'

    def get_context_data(self, **kwargs):
        kwargs["events"] = Event.objects.all()
        return super().get_context_data(**kwargs)


class AdminCheckInStatusView(AdministratorMixin, CheckInStatusView):
    pass


class AssistantCheckInStatusView(AssistantMixin, CheckInStatusView):
    pass


class PublicCheckInStatusView(PublicTournamentPageMixin, CheckInStatusView):
    public_page_preference = 'public_checkins'


class CheckInIdentifiersView(TournamentMixin, TemplateView):
    template_name = 'checkin_ids.html'
    page_title = _('Identifiers Overview')
    page_emoji = '📛'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        kwargs["peopleWithIDs"] = PersonIdentifier.objects.count()
        kwargs["allPeople"] = t.adjudicator_set.count() + Speaker.objects.filter(team__tournament=t).count()
        kwargs["venuesWithIDs"] = VenueIdentifier.objects.filter(venue__tournament=t).count()
        kwargs["allVenues"] = t.venue_set.count()
        return super().get_context_data(**kwargs)


class AdminCheckInIdentifiersView(AdministratorMixin, CheckInIdentifiersView):
    pass


class AssistantCheckInIdentifiersView(AssistantMixin, CheckInIdentifiersView):
    pass
