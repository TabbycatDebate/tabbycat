from django.views.generic.base import TemplateView

from utils.mixins import AdministratorMixin, AssistantMixin
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin


class CheckInScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'


class AdminCheckInScanView(AdministratorMixin, CheckInScanView):
    pass


class AssistantCheckInScanView(AssistantMixin, CheckInScanView):
    pass


class CheckInStatusView(TournamentMixin, TemplateView):
    template_name = 'checkin_status.html'


class AdminCheckInStatusView(AdministratorMixin, CheckInStatusView):
    pass


class AssistantCheckInStatusView(AssistantMixin, CheckInStatusView):
    pass


class PublicCheckInStatusView(PublicTournamentPageMixin, CheckInStatusView):
    public_page_preference = 'public_checkins'
