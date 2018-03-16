import json

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from participants.models import Speaker
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin, CacheMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView, PostOnlyRedirectView
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import Event, Identifier, PersonIdentifier, VenueIdentifier
from .utils import create_identifiers, get_unexpired_checkins


class CheckInPreScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'
    page_title = _('Scan Identifiers')
    page_emoji = '📷'

    def get_context_data(self, **kwargs):
        kwargs["scan_url"] = reverse_tournament(self.scan_view, self.tournament)
        return super().get_context_data(**kwargs)


class AdminCheckInPreScanView(AdministratorMixin, CheckInPreScanView):
    scan_view = 'admin-checkin-scan'


class AssistantCheckInPreScanView(AssistantMixin, CheckInPreScanView):
    scan_view = 'assistant-checkin-scan'


class CheckInScanView(JsonDataResponsePostView, TournamentMixin):

    def post_data(self):
        barcode_ids = json.loads(self.body)['barcodes']
        for barcode in barcode_ids:
            try:
                identifier = Identifier.objects.get(barcode=barcode)
                event = Event.objects.create(identifier=identifier,
                                             tournament=self.tournament)
            except ObjectDoesNotExist:
                raise BadJsonRequestError("Identifier doesn't exist")

        return json.dumps({'ids': barcode_ids,
                           'time': event.time.strftime('%H:%M:%S')})


class AdminCheckInScanView(AdministratorMixin, CheckInScanView):
    pass


class AssistantCheckInScanView(AssistantMixin, CheckInScanView):
    pass


class BaseCheckInStatusView(TournamentMixin, TemplateView):
    template_name = 'checkin_status.html'
    scan_view = False

    def get_context_data(self, **kwargs):
        events = get_unexpired_checkins(self.tournament)
        kwargs["events"] = json.dumps([e.serialize() for e in events])
        if self.scan_view:
            kwargs["scan_url"] = reverse_tournament(self.scan_view, self.tournament)
        return super().get_context_data(**kwargs)


class CheckInPeopleStatusView(BaseCheckInStatusView):
    page_emoji = '⌚️'
    page_title = _("People's Check-In Statuses")

    def get_context_data(self, **kwargs):

        adjudicators = []
        for adj in self.tournament.relevant_adjudicators.select_related('institution', 'checkin_identifier'):
            adj_dict = {
                'id': adj.id,
                'name': adj.name,
                'type': 'Adjudicator',
                'institution': adj.institution.serialize if adj.institution else None,
            }
            try:
                adj_dict['identifier'] = adj.checkin_identifier.barcode
            except ObjectDoesNotExist:
                pass
            adjudicators.append(adj_dict)
        kwargs["adjudicators"] = json.dumps(adjudicators)

        speakers = []
        for speaker in Speaker.objects.filter(team__tournament=self.tournament).select_related('team', 'team__institution', 'checkin_identifier'):
            speaker_dict = {
                'id': speaker.id,
                'name': speaker.name,
                'type': 'Speaker',
                'institution': speaker.team.institution.serialize if speaker.team.institution else None,
                'team': speaker.team.short_name,
            }
            try:
                speaker_dict['identifier'] = speaker.checkin_identifier.barcode
            except ObjectDoesNotExist:
                pass
            speakers.append(speaker_dict)
        kwargs["speakers"] = json.dumps(speakers)

        return super().get_context_data(**kwargs)


class AdminCheckInPeopleStatusView(AdministratorMixin, CheckInPeopleStatusView):
    scan_view = 'admin-checkin-scan'


class AssistantCheckInPeopleStatusView(AssistantMixin, CheckInPeopleStatusView):
    scan_view = 'assistant-checkin-scan'


class PublicCheckInPeopleStatusView(PublicTournamentPageMixin, CacheMixin,
                                    CheckInPeopleStatusView):
    public_page_preference = 'public_checkins'


class CheckInVenuesStatusView(BaseCheckInStatusView):
    page_emoji = '👜'
    page_title = _("Venue's Check-In Statuses")

    def get_context_data(self, **kwargs):
        venues = []
        for venue in self.tournament.relevant_venues.select_related('checkin_identifier').prefetch_related('venuecategory_set').all():
            item = venue.serialize()
            try:
                item['identifier'] = venue.checkin_identifier.barcode
            except ObjectDoesNotExist:
                pass
            venues.append(item)
        kwargs["venues"] = json.dumps(venues)

        return super().get_context_data(**kwargs)


class AdminCheckInVenuesStatusView(AdministratorMixin, CheckInVenuesStatusView):
    scan_view = 'admin-checkin-scan'


class AssistantCheckInVenuesStatusView(AssistantMixin, CheckInVenuesStatusView):
    scan_view = 'assistant-checkin-scan'


class SegregatedCheckinsMixin(TournamentMixin):

    def t_speakers(self):
        return Speaker.objects.filter(
            team__tournament=self.tournament).values_list(
            'person_ptr_id', flat=True)

    def speakers_with_barcodes(self):
        identifiers = PersonIdentifier.objects.all()
        return identifiers.filter(person_id__in=self.t_speakers())

    def t_adjs(self):
        return self.tournament.adjudicator_set.values_list(
            'person_ptr_id', flat=True)

    def adjs_with_barcodes(self):
        identifiers = PersonIdentifier.objects.all()
        return identifiers.filter(person_id__in=self.t_adjs())


class CheckInIdentifiersView(SegregatedCheckinsMixin, TemplateView):
    template_name = 'checkin_ids.html'
    page_title = _('Make Identifiers')
    page_emoji = '📛'

    def get_context_data(self, **kwargs):
        t = self.tournament
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

    # Providing tournament_slug_url_kwarg isn't working for some reason; so use:
    def get_redirect_url(self, *args, **kwargs):
        return reverse_tournament('admin-checkin-identifiers', self.tournament)

    def post(self, request, *args, **kwargs):
        t = self.tournament

        if self.kwargs["kind"] == "speakers":
            create_identifiers(PersonIdentifier, Speaker.objects.filter(team__tournament=t))
        elif self.kwargs["kind"] == "adjudicators":
            create_identifiers(PersonIdentifier, t.adjudicator_set.all())
        elif self.kwargs["kind"] == "venues":
            create_identifiers(VenueIdentifier, t.venue_set.all())

        messages.success(request, _("Generated identifiers for %s" % self.kwargs["kind"]))
        self.log_action()  # Need to call explicitly
        return super().post(request, *args, **kwargs)


class CheckInPrintablesView(SegregatedCheckinsMixin, TemplateView):
    template_name = 'checkin_printables.html'
    page_title = _('Identifiers')
    page_emoji = '📛'

    def get_context_data(self, **kwargs):
        if self.kwargs["kind"] == "speakers":
            kwargs["identifiers"] = self.speakers_with_barcodes().order_by('person__name')
        elif self.kwargs["kind"] == "adjudicators":
            kwargs["identifiers"] = self.adjs_with_barcodes().order_by('person__name')
        elif self.kwargs["kind"] == "venues":
            venues = self.tournament.relevant_venues
            kwargs["identifiers"] = VenueIdentifier.objects.filter(venue__in=venues)

        return super().get_context_data(**kwargs)


class AdminCheckInPrintablesView(AdministratorMixin, CheckInPrintablesView):
    pass


class AssistantCheckInPrintablesView(AssistantMixin, CheckInPrintablesView):
    pass
