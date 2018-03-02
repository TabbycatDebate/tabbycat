from django.views.generic.base import TemplateView

from utils.mixins import AdministratorMixin, AssistantMixin
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import Event, PersonIdentifier


class CheckInScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'


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

    def get_context_data(self, **kwargs):
        kwargs["identifiers"] = PersonIdentifier.objects.all()
        return super().get_context_data(**kwargs)


class AdminCheckInIdentifiersView(AdministratorMixin, CheckInIdentifiersView):
    pass


class AssistantCheckInIdentifiersView(AssistantMixin, CheckInIdentifiersView):
    pass
