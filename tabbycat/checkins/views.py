import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from options.utils import use_team_code_names
from participants.models import Person, Speaker
from participants.serializers import InstitutionSerializer
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.views import PostOnlyRedirectView
from venues.serializers import VenueSerializer

from .consumers import CheckInEventConsumer
from .models import Event, PersonIdentifier, VenueIdentifier
from .utils import create_identifiers, get_unexpired_checkins


class CheckInPreScanView(TournamentMixin, TemplateView):
    template_name = 'checkin_scan.html'
    page_title = _('Scan Identifiers')
    page_emoji = '📷'

    def get_context_data(self, **kwargs):
        kwargs["scan_url"] = self.tournament.slug + '/checkins/'
        return super().get_context_data(**kwargs)


class AdminCheckInPreScanView(AdministratorMixin, CheckInPreScanView):
    scan_view = 'admin-checkin-scan'


class AssistantCheckInPreScanView(AssistantMixin, CheckInPreScanView):
    scan_view = 'assistant-checkin-scan'


class BaseCheckInStatusView(TournamentMixin, TemplateView):
    template_name = 'checkin_status.html'
    scan_view = False
    for_admin = True

    def get_context_data(self, **kwargs):
        events = get_unexpired_checkins(self.tournament, self.window_preference)
        kwargs["events"] = json.dumps([e.serialize() for e in events])
        if self.scan_view:
            kwargs["scan_url"] = self.tournament.slug + '/checkins/'
        kwargs["for_admin"] = self.for_admin
        kwargs["team_size"] = self.tournament.pref('substantive_speakers')
        return super().get_context_data(**kwargs)


class CheckInPeopleStatusView(BaseCheckInStatusView):
    page_emoji = '⌚️'
    page_title = _("People's Check-In Statuses")
    window_preference = 'checkin_window_people'

    def get_context_data(self, **kwargs):

        team_codes = use_team_code_names(self.tournament, admin=self.for_admin)
        kwargs["team_codes"] = json.dumps(team_codes)

        adjudicators = []
        for adj in self.tournament.relevant_adjudicators.all().select_related('institution', 'checkin_identifier'):
            try:
                code = adj.checkin_identifier.barcode
            except ObjectDoesNotExist:
                code = None

            institution = InstitutionSerializer(adj.institution).data if adj.institution else None
            adjudicators.append({
                'id': adj.id, 'name': adj.name, 'type': 'Adjudicator',
                'identifier': [code], 'locked': False, 'independent': adj.independent,
                'institution': institution,
            })
        kwargs["adjudicators"] = json.dumps(adjudicators)

        speakers = []
        for speaker in Speaker.objects.filter(team__tournament=self.tournament).select_related('team', 'team__institution', 'checkin_identifier'):
            try:
                code = speaker.checkin_identifier.barcode
            except ObjectDoesNotExist:
                code = None

            institution = InstitutionSerializer(speaker.team.institution).data if speaker.team.institution else None
            speakers.append({
                'id': speaker.id, 'name': speaker.name, 'type': 'Speaker',
                'identifier': [code], 'locked': False,
                'team': speaker.team.code_name if team_codes else speaker.team.short_name,
                'institution': institution,
            })
        kwargs["speakers"] = json.dumps(speakers)

        return super().get_context_data(**kwargs)


class AdminCheckInPeopleStatusView(AdministratorMixin, CheckInPeopleStatusView):
    scan_view = 'admin-checkin-scan'


class AssistantCheckInPeopleStatusView(AssistantMixin, CheckInPeopleStatusView):
    scan_view = 'assistant-checkin-scan'


class PublicCheckInPeopleStatusView(PublicTournamentPageMixin, CheckInPeopleStatusView):
    for_admin = False
    public_page_preference = 'public_checkins'


class CheckInVenuesStatusView(BaseCheckInStatusView):
    page_emoji = '👜'
    page_title = _("Rooms' Check-In Statuses")
    window_preference = 'checkin_window_venues'

    def get_context_data(self, **kwargs):
        venues = []
        for venue in self.tournament.relevant_venues.select_related('checkin_identifier').prefetch_related('venuecategory_set').all():
            item = VenueSerializer(venue).data
            item['locked'] = False
            try:
                item['identifier'] = [venue.checkin_identifier.barcode]
            except ObjectDoesNotExist:
                item['identifier'] = [None]
            venues.append(item)
        kwargs["venues"] = json.dumps(venues)
        kwargs["team_codes"] = json.dumps(False)

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
                "in":  self.speakers_with_barcodes().count(),
            },
            "adjudicators": {
                "title": _("Adjudicators"),
                "total": self.t_adjs().count(),
                "in":  self.adjs_with_barcodes().count(),
            },
            "venues": {
                "title": _("Rooms"),
                "total": t.venue_set.count(),
                "in":  VenueIdentifier.objects.filter(venue__tournament=t).count(),
            },
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


class ParticipantCheckinView(PublicTournamentPageMixin, PostOnlyRedirectView):

    public_page_preference = 'public_checkins_submit'

    def post(self, request, *args, **kwargs):
        t = self.tournament

        action = request.POST['action']

        try:
            person = Person.objects.get(url_key=kwargs['url_key'])
            identifier = person.checkin_identifier
        except Person.DoesNotExist:
            raise Http404("Person does not exist")
        except PersonIdentifier.DoesNotExist:
            messages.error(request, _("Could not check you in as you do not have an identifying code — your tab director may need to make you an identifier."))
            return super().post(request, *args, **kwargs)

        existing_checkin = get_unexpired_checkins(t, 'checkin_window_people').filter(identifier=identifier)
        if action == 'revoke':
            if existing_checkin.exists():
                existing_checkin.delete()
                checkin_dict = {'identifier': identifier.barcode}
                messages.success(request, _("You have revoked your check-in."))
            else:
                messages.error(request, _("Whoops! Looks like your check-in was already revoked."))
                return super().post(request, *args, **kwargs)
        elif action == 'checkin':
            if existing_checkin.exists():
                messages.error(request, _("Whoops! Looks like you're already checked in."))
                return super().post(request, *args, **kwargs)
            else:
                checkin = Event.objects.create(identifier=identifier,
                                               tournament=self.tournament)
                checkin_dict = checkin.serialize()
                checkin_dict['owner_name'] = person.name
                messages.success(request, _("You are now checked in."))
        else:
            return TemplateResponse(request=self.request, template='400.html', status=400)

        # Override permissions check - no user but authenticated through URL
        group_name = CheckInEventConsumer.group_prefix + "_" + t.slug
        async_to_sync(get_channel_layer().group_send)(
            group_name, {
                'type': 'send_json',
                'data': {
                    'checkins': [checkin_dict],
                },
            },
        )

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': kwargs['url_key']})
