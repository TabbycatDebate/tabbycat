from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from participants.models import Speaker
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.views import JsonDataResponsePostView, PostOnlyRedirectView
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import Event, Identifier, PersonIdentifier, VenueIdentifier


class CheckInScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'
    page_title = _('Scan Identifiers')
    page_emoji = '📷'


class AdminCheckInScanView(AdministratorMixin, CheckInScanView):
    pass


class AssistantCheckInScanView(AssistantMixin, CheckInScanView):
    pass


class CheckInIdentifier(JsonDataResponsePostView):

    def post_data(self):
        barcode_id = self.request.POST.get('barcode')
        print(barcode_id)
        identifier = Identifier.objects.filter(identifier=barcode_id)

        print(identifier)

        return {

        }


class CheckInStatusView(TournamentMixin, TemplateView):
    template_name = 'checkin_status.html'
    page_title = _('Check In Statuses')
    page_emoji = '⌚️'

    def get_context_data(self, **kwargs):
        kwargs["events"] = Event.objects.all()
        return super().get_context_data(**kwargs)


class AdminCheckInStatusView(AdministratorMixin, CheckInStatusView):
    pass


class AssistantCheckInStatusView(AssistantMixin, CheckInStatusView):
    pass


class PublicCheckInStatusView(PublicTournamentPageMixin, CheckInStatusView):
    public_page_preference = 'public_checkins'


class SegregatedCheckinsMixin(TournamentMixin):

    def t_speakers(self):
        return Speaker.objects.filter(
            team__tournament=self.get_tournament()).values_list(
            'person_ptr_id', flat=True)

    def speakers_with_barcodes(self):
        identifiers = PersonIdentifier.objects.all()
        return identifiers.filter(person_id__in=self.t_speakers())

    def t_adjs(self):
        return self.get_tournament().adjudicator_set.values_list(
            'person_ptr_id', flat=True)

    def adjs_with_barcodes(self):
        identifiers = PersonIdentifier.objects.all()
        return identifiers.filter(person_id__in=self.t_adjs())


class CheckInIdentifiersView(SegregatedCheckinsMixin, TemplateView):
    template_name = 'checkin_ids.html'
    page_title = _('Identifiers Overview')
    page_emoji = '📛'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        kwargs["check_in_info"] = {
            "speakers": {
                "title": _("Speakers"),
                "total": self.t_speakers().count(),
                "in":  self.speakers_with_barcodes().count()
            },
            "adjudicators": {
                "title": _("Adjudicators"),
                "total": self.t_adjs().count(),
                "in":  self.adjs_with_barcodes().count()
            },
            "venues": {
                "title": _("Venues"),
                "total": t.venue_set.count(),
                "in":  VenueIdentifier.objects.filter(venue__tournament=t).count(),
            }
        }
        return super().get_context_data(**kwargs)


class AdminCheckInIdentifiersView(AdministratorMixin, CheckInIdentifiersView):
    pass


class AssistantCheckInIdentifiersView(AssistantMixin, CheckInIdentifiersView):
    pass


class AdminCheckInGenerateView(AdministratorMixin, LogActionMixin,
                               TournamentMixin, PostOnlyRedirectView):

    def get_action_log_type(self):
        if self.kwargs["kind"] == "speakers":
            return ActionLogEntry.ACTION_TYPE_CHECKIN_SPEAK_GENERATE
        elif self.kwargs["kind"] == "adjudicators":
            return ActionLogEntry.ACTION_TYPE_CHECKIN_ADJ_GENERATE
        elif self.kwargs["kind"] == "venues":
            return ActionLogEntry.ACTION_TYPE_CHECKIN_VENUES_GENERATE

    def create_ids(self, model_to_make, items_to_check):
        kind = model_to_make.instance_attr
        for item in list(items_to_check):
            try:
                model_to_make.objects.get(**{kind: item})
            except ObjectDoesNotExist:
                model_to_make.objects.create(**{kind: item})

        return

    # Providing tournament_slug_url_kwarg isn't working for some reason; so use:
    def get_redirect_url(self, *args, **kwargs):
        return reverse_tournament('admin-checkin-identifiers', self.get_tournament())

    def post(self, request, *args, **kwargs):
        t = self.get_tournament()

        if self.kwargs["kind"] == "speakers":
            self.create_ids(PersonIdentifier, Speaker.objects.filter(team__tournament=t))
        elif self.kwargs["kind"] == "adjudicators":
            self.create_ids(PersonIdentifier, t.adjudicator_set.all())
        elif self.kwargs["kind"] == "venues":
            self.create_ids(VenueIdentifier, t.venue_set.all())

        messages.success(request, _("Generated identifiers for %s" % self.kwargs["kind"]))
        self.log_action()  # Need to call explicitly
        return super().post(request, *args, **kwargs)


class CheckInPrintablesView(SegregatedCheckinsMixin, TemplateView):
    template_name = 'checkin_printables.html'
    page_title = _('Identifiers')
    page_emoji = '📛'

    def get_context_data(self, **kwargs):
        if self.kwargs["kind"] == "speakers":
            kwargs["identifiers"] = self.speakers_with_barcodes()
        elif self.kwargs["kind"] == "adjudicators":
            kwargs["identifiers"] = self.adjs_with_barcodes()
        elif self.kwargs["kind"] == "venue":
            kwargs["identifiers"] = VenueIdentifier.objects.all()

        return super().get_context_data(**kwargs)


class AdminCheckInPrintablesView(AdministratorMixin, CheckInPrintablesView):
    pass


class AssistantCheckInPrintablesView(AssistantMixin, CheckInPrintablesView):
    pass
