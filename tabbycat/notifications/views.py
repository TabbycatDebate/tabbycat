import json
import logging
from datetime import datetime
from smtplib import SMTPException, SMTPResponseException
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import formats, timezone
from django.utils.html import escape
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.base import View
from django.views.generic.edit import FormView

from participants.models import Person
from tournaments.mixins import RoundMixin, TournamentMixin
from utils.mixins import AdministratorMixin, WarnAboutLegacySendgridConfigVarsMixin
from utils.tables import TabbycatTableBuilder
from utils.views import VueTableTemplateView

from .forms import BasicEmailForm, TestEmailForm
from .models import BulkNotification, EmailStatus, SentMessage

if TYPE_CHECKING:
    from django.http.response import HttpResponseRedirect
    from django.db.models import QuerySet
    from django.http.request import HttpRequest

logger = logging.getLogger(__name__)


class TestEmailView(WarnAboutLegacySendgridConfigVarsMixin, AdministratorMixin, FormView):
    form_class = TestEmailForm
    template_name = 'test_email.html'
    success_url = reverse_lazy('notifications-test-email')
    view_role = ""

    def form_valid(self, form: TestEmailForm) -> 'HttpResponseRedirect':
        host = self.request.get_host()

        try:
            recipient = form.send_email(host)

        except SMTPResponseException as e:
            try:
                smtp_error = e.smtp_error.decode()  # it seems to be a bytes object
            except (AttributeError, UnicodeDecodeError):
                smtp_error = str(e.smtp_error)      # but just in case it's not, fall back to generic str()
            messages.error(self.request, _("The email (SMTP) server returned an error sending the test email: "
                "[SMTP code %(code)d] %(error)s") % {
                'code': e.smtp_code, 'error': smtp_error})
            if e.smtp_code == 550 and "Sender Identity" in smtp_error:
                messages.warning(self.request, _("Hint: If the error is about sender identity verification in SendGrid, "
                    "and you've already completed the steps in SendGrid, it may be that you need to update "
                    "the DEFAULT_FROM_EMAIL config var in Heroku to match your verified sender identity."))
                logger.warning("Suspected SendGrid sender identity verification error in test email", exc_info=True)
            else:
                logger.warning("SMTP response exception in test email", exc_info=True)

        except (ConnectionError, SMTPException) as e:
            messages.error(self.request,
                _("There was an error sending the test email: %(error)s") % {'error': str(e)})
            logger.warning("Other error in test email", exc_info=True)

        else:
            messages.success(self.request,
                _("A test email has been sent to %(recipient)s.") % {'recipient': recipient})

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        kwargs["default_from_email"] = settings.DEFAULT_FROM_EMAIL
        return super().get_context_data(**kwargs)


class EmailStatusView(AdministratorMixin, TournamentMixin, VueTableTemplateView):
    page_title = gettext_lazy("Email Statuses")
    page_emoji = '📤'
    template_name = 'email_statuses.html'

    tables_orientation = 'rows'

    NA_CELL = {'text': _("N/A"), 'class': 'text-muted'}
    UNKNOWN_RECIPIENT_CELL = {'text': _("Not known"), 'class': 'text-muted'}

    def _create_status_timeline(self, status: List[EmailStatus]) -> List[Dict[str, str]]:
        statuses = []
        for s in status:
            text = _("%(status)s @ %(time)s") % {
                'status': s.get_event_display(),
                'time': formats.time_format(timezone.localtime(s.timestamp), use_l10n=True),
            }
            statuses.append({
                'text': '<span class="%s">%s</span>' % (self._get_event_class(s.event), text),
            })
        return statuses

    def _get_event_class(self, event: EmailStatus.EventType) -> Optional[str]:
        return {
            EmailStatus.EventType.BOUNCED: 'text-warning',
            EmailStatus.EventType.DROPPED: 'text-warning',
            EmailStatus.EventType.SPAM: 'text-warning',
            EmailStatus.EventType.DEFERRED: 'text-warning',
            EmailStatus.EventType.PROCESSED: 'text-info',
            EmailStatus.EventType.DELIVERED: 'text-info',
            EmailStatus.EventType.OPENED: 'text-success',
            EmailStatus.EventType.CLICKED: 'text-success',
            EmailStatus.EventType.UNSUBSCRIBED: None,
            EmailStatus.EventType.ASM_UNSUBSCRIBED: None,
            EmailStatus.EventType.ASM_RESUBSCRIBED: None,
        }[event]

    def get_tables(self) -> List[TabbycatTableBuilder]:
        tables = []

        # notifications.sentmessage_set.first().emailstatus_set.first().latest_statuses will be a list
        notifications = self.tournament.bulknotification_set.select_related(
            'round',
        ).prefetch_related(Prefetch(
            'sentmessage_set',
            queryset=SentMessage.objects.select_related(
                'recipient',
            ).prefetch_related(Prefetch(
                'emailstatus_set',
                queryset=EmailStatus.objects.order_by('-timestamp'),
                to_attr='statuses',
            )),
        ))

        for notification in notifications:

            if notification.round is not None:
                subtitle = notification.round.name
            else:
                subtitle = _("@ %s") % formats.time_format(timezone.localtime(notification.timestamp), use_l10n=True)

            table = TabbycatTableBuilder(view=self, title=notification.get_event_display().capitalize(), subtitle=subtitle)

            emails_recipient = []
            emails_addresses = []
            emails_status = []
            emails_time = []

            for sentmessage in notification.sentmessage_set.all():
                emails_recipient.append(escape(sentmessage.recipient.name) if sentmessage.recipient else self.UNKNOWN_RECIPIENT_CELL)
                emails_addresses.append(escape(sentmessage.email) or self.UNKNOWN_RECIPIENT_CELL)

                if len(sentmessage.statuses) > 0:
                    latest_status = sentmessage.statuses[0]  # already ordered
                    status_cell = {
                        "text": latest_status.get_event_display(),
                        "class": self._get_event_class(latest_status.event),
                        "popover": {
                            "title": _("Timeline"),
                            "content": self._create_status_timeline(sentmessage.statuses),
                        },
                    }
                    emails_status.append(status_cell)
                    emails_time.append(formats.time_format(timezone.localtime(latest_status.timestamp), use_l10n=True))
                else:
                    emails_status.append(self.NA_CELL)
                    emails_time.append(self.NA_CELL)

            table.add_column({'key': 'name', 'tooltip': _("Participant"), 'icon': 'user'}, emails_recipient)
            table.add_column({'key': 'email', 'tooltip': _("Email address"), 'icon': 'mail'}, emails_addresses)
            table.add_column({'key': 'name', 'title': _("Status")}, emails_status)
            table.add_column({'key': 'name', 'title': _("Time")}, emails_time)

            tables.append(table)

        return tables


class EmailEventWebhookView(TournamentMixin, View):

    def post(self, request: 'HttpRequest', *args, **kwargs) -> HttpResponse:
        if not self.tournament.pref('email_hook_key'):
            return HttpResponse(status=403) # 403: Forbidden

        if kwargs['key'] != self.tournament.pref('email_hook_key'):
            return HttpResponse(status=403) # 403: Forbidden

        data = json.loads(request.body)

        # Ignore all objects without a Tabbycat-specified hook ID
        data = [obj for obj in data if 'hook-id' in obj and obj['hook-id'] is not None]
        records = SentMessage.objects.filter(hook_id__in=[obj['hook-id'] for obj in data])
        record_lookup = {smr.hook_id: smr.id for smr in records}
        statuses = []

        for obj in data:
            dt = datetime.fromtimestamp(obj['timestamp'])
            timestamp = timezone.make_aware(dt, timezone.utc)
            email_id = record_lookup.get(obj['hook-id'], None)
            if email_id is None:
                continue
            statuses.append(EmailStatus(email_id=email_id, timestamp=timestamp, event=obj['event'], data=obj))

        EmailStatus.objects.bulk_create(statuses)

        return HttpResponse(status=201) # 201: Created


class BaseSelectPeopleEmailView(AdministratorMixin, TournamentMixin, VueTableTemplateView, FormView):
    template_name = "email_participants.html"
    page_title = gettext_lazy("Email Participants")
    page_emoji = '📤'

    form_class = BasicEmailForm

    def get_success_url(self, *args, **kwargs) -> str:
        return self.get_redirect_url(*args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sg_webhook'] = EmailStatus.objects.filter(email__notification__tournament=self.tournament).exists()

        context['categories'] = [{'id': 'spk', 'name': "Email"}]
        return context

    def get_default_send_queryset(self) -> 'QuerySet[Person]':
        return self.get_queryset().filter(email__isnull=False).exclude(email__exact="")

    def get_queryset(self) -> 'QuerySet[Person]':
        """All the people from the tournament who could receive the message"""
        queryset_filter = Q(speaker__team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)

        return Person.objects.filter(queryset_filter).select_related('speaker', 'adjudicator')

    def default_send(self, p: Person, default_send_queryset: Optional['QuerySet[Person]'] = None) -> bool:
        """Whether the person should be emailed by default"""
        return p in default_send_queryset

    def add_sent_notification(self, email_count: int) -> None:
        text = ngettext("%(email_count)s email has been queued for sending.",
                        "%(email_count)s emails have been queued for sending.",
                        email_count) % {'email_count': email_count}
        if email_count > 0:
            messages.success(self.request, text)
        else:
            messages.warning(self.request, _("No emails were sent — likely because no recipients were selected."))

    def get_person_type(self, person: Person, **kwargs) -> str:
        return 'adj' if kwargs['mixed'] and hasattr(person, 'adjudicator') else 'spk'

    def get_table(self, mixed_participants: bool = False) -> TabbycatTableBuilder:
        table = TabbycatTableBuilder(view=self, sort_key='name')

        queryset = self.get_queryset()
        default_send_queryset = self.get_default_send_queryset()

        table.add_column({'key': 'send', 'title': _("Send Email")}, [{
            'component': 'check-cell',
            'checked': self.default_send(p, default_send_queryset),
            'id': p.id,
            'name': 'recipients',
            'value': p.id,
            'noSave': True,
            'type': self.get_person_type(p, mixed=mixed_participants),
        } for p in queryset])

        table.add_column({'key': 'name', 'tooltip': _("Participant"), 'icon': 'user'}, [{
            'text': escape(p.name),
            'class': 'no-wrap' if len(p.name) < 20 else '',
        } for p in queryset])

        table.add_column({'key': 'email', 'tooltip': _("Email address"), 'icon': 'mail'}, [{
            'text': escape(p.email) if p.email else _("Not Provided"),
            'class': 'small' if p.email else 'small text-warning',
        } for p in queryset])

        return table


class RoleColumnMixin:
    """Mixin to have a column Adjudicator/Speaker for email"""

    def get_table(self, mixed_participants: bool = True) -> TabbycatTableBuilder:
        table = super().get_table(mixed_participants)

        table.add_column({'key': 'role', 'title': _("Role")}, [{
            'text': _("Adjudicator") if hasattr(p, 'adjudicator') else _("Speaker"),
        } for p in self.get_queryset()])

        return table

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'id': 'spk', 'name': _("Speakers")},
            {'id': 'adj', 'name': _("Adjudicators")},
        ]
        return context


class TemplateEmailCreateView(BaseSelectPeopleEmailView):

    def get_initial(self) -> Dict[str, str]:
        initial = super().get_initial()
        initial['subject_line'] = self.tournament.pref(self.subject_template)
        initial['message_body'] = self.tournament.pref(self.message_template)

        return initial

    def form_valid(self, form: BasicEmailForm) -> 'HttpResponseRedirect':
        if hasattr(self, 'subject_template'):
            self.tournament.preferences[self.subject_template] = form.cleaned_data['subject_line']
            self.tournament.preferences[self.message_template] = form.cleaned_data['message_body']
        email_recipients = list(map(int, self.request.POST.getlist('recipients')))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email",
            "message": self.event,
            "extra": self.get_extra(),
            "send_to": email_recipients,
            "subject": form.cleaned_data['subject_line'],
            "body": form.cleaned_data['message_body'],
        })

        self.add_sent_notification(len(email_recipients))
        return super().form_valid(form)


class TournamentTemplateEmailCreateView(TemplateEmailCreateView):

    def get_default_send_queryset(self) -> 'QuerySet[Person]':
        return super().get_default_send_queryset().exclude(
            sentmessage__notification__event=self.event, sentmessage__notification__tournament=self.tournament)

    def get_extra(self) -> Dict[str, Any]:
        extra = {'tournament_id': self.tournament.id}
        return extra


class CustomEmailCreateView(RoleColumnMixin, TournamentTemplateEmailCreateView):
    tournament_redirect_pattern_name = 'notifications-email'
    event = BulkNotification.EventType.CUSTOM

    def get_initial(self) -> Dict[str, str]:
        return {}  # Have everything unset

    def get_default_send_queryset(self) -> 'QuerySet[Person]':
        # From TemplateEmailCreateView to avoid excluding if already got custom
        return self.get_queryset().filter(email__isnull=False).exclude(email__exact="")

    def default_send(self, p: Person, default_send_queryset: 'QuerySet[Person]') -> bool:
        return False


class RoundTemplateEmailCreateView(TemplateEmailCreateView, RoundMixin):

    def get_default_send_queryset(self) -> 'QuerySet[Person]':
        return super().get_default_send_queryset().exclude(
            sentmessage__notification__event=self.event, sentmessage__notification__round=self.round)

    def get_extra(self) -> Dict[str, Any]:
        extra = {'round_id': self.round.id}
        return extra
