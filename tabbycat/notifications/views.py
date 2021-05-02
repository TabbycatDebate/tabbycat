import json
from datetime import datetime
from smtplib import SMTPException

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import formats, timezone
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.base import View
from django.views.generic.edit import FormView

from participants.models import Person
from tournaments.mixins import RoundMixin, TournamentMixin
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import VueTableTemplateView

from .forms import BasicEmailForm, TestEmailForm
from .models import EmailStatus, SentMessage


class TestEmailView(AdministratorMixin, FormView):
    form_class = TestEmailForm
    template_name = 'test_email.html'
    success_url = reverse_lazy('notifications-test-email')
    view_role = ""

    def form_valid(self, form):
        host = self.request.get_host()
        try:
            recipient = form.send_email(host)
        except (ConnectionError, SMTPException) as e:
            messages.error(self.request,
                _("There was an error sending the test email: %(error)s") % {'error': str(e)})
        else:
            messages.success(self.request,
                _("A test email has been sent to %(recipient)s.") % {'recipient': recipient})
        return super().form_valid(form)


class EmailStatusView(AdministratorMixin, TournamentMixin, VueTableTemplateView):
    page_title = gettext_lazy("Email Statuses")
    page_emoji = '📤'
    template_name = 'email_statuses.html'

    tables_orientation = 'rows'

    NA_CELL = {'text': _("N/A"), 'class': 'text-muted'}
    UNKNOWN_RECIPIENT_CELL = {'text': _("Not known"), 'class': 'text-muted'}

    def _create_status_timeline(self, status):
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

    def _get_event_class(self, event):
        return {
            EmailStatus.EVENT_TYPE_BOUNCED: 'text-warning',
            EmailStatus.EVENT_TYPE_DROPPED: 'text-warning',
            EmailStatus.EVENT_TYPE_SPAM: 'text-warning',
            EmailStatus.EVENT_TYPE_DEFERRED: 'text-warning',
            EmailStatus.EVENT_TYPE_PROCESSED: 'text-info',
            EmailStatus.EVENT_TYPE_DELIVERED: 'text-info',
            EmailStatus.EVENT_TYPE_OPENED: 'text-success',
            EmailStatus.EVENT_TYPE_CLICKED: 'text-success',
            EmailStatus.EVENT_TYPE_UNSUBSCRIBED: None,
            EmailStatus.EVENT_TYPE_ASM_UNSUBSCRIBED: None,
            EmailStatus.EVENT_TYPE_ASM_RESUBSCRIBED: None,
        }[event]

    def get_tables(self):
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
                emails_recipient.append(sentmessage.recipient.name if sentmessage.recipient else self.UNKNOWN_RECIPIENT_CELL)
                emails_addresses.append(sentmessage.email or self.UNKNOWN_RECIPIENT_CELL)

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

    def post(self, request, *args, **kwargs):
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

    def get_success_url(self, *args, **kwargs):
        return self.get_redirect_url(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sg_webhook'] = EmailStatus.objects.filter(email__notification__tournament=self.tournament).exists()

        context['categories'] = [{'id': 'spk', 'name': "Email"}]
        return context

    def get_default_send_queryset(self):
        return self.get_queryset().filter(email__isnull=False).exclude(email__exact="")

    def get_queryset(self):
        """All the people from the tournament who could receive the message"""
        queryset_filter = Q(speaker__team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)

        return Person.objects.filter(queryset_filter).select_related('speaker', 'adjudicator')

    def default_send(self, p, default_send_queryset=None):
        """Whether the person should be emailed by default"""
        return p in default_send_queryset

    def add_sent_notification(self, email_count):
        text = ngettext("%(email_count)s email has been queued for sending.",
                        "%(email_count)s emails have been queued for sending.",
                        email_count) % {'email_count': email_count}
        if email_count > 0:
            messages.success(self.request, text)
        else:
            messages.warning(self.request, _("No emails were sent — likely because no recipients were selected."))

    def get_person_type(self, person, **kwargs):
        return 'adj' if kwargs['mixed'] and hasattr(person, 'adjudicator') else 'spk'

    def get_table(self, mixed_participants=False):
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
            'text': p.name,
            'class': 'no-wrap' if len(p.name) < 20 else '',
        } for p in queryset])

        table.add_column({'key': 'email', 'tooltip': _("Email address"), 'icon': 'mail'}, [{
            'text': p.email if p.email else _("Not Provided"),
            'class': 'small' if p.email else 'small text-warning',
        } for p in queryset])

        return table


class RoleColumnMixin:
    """Mixin to have a column Adjudicator/Speaker for email"""

    def get_table(self, mixed_participants=True):
        table = super().get_table(mixed_participants)

        table.add_column({'key': 'role', 'title': _("Role")}, [{
            'text': _("Adjudicator") if hasattr(p, 'adjudicator') else _("Speaker"),
        } for p in self.get_queryset()])

        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'id': 'spk', 'name': _("Speakers")},
            {'id': 'adj', 'name': _("Adjudicators")},
        ]
        return context


class CustomEmailCreateView(RoleColumnMixin, BaseSelectPeopleEmailView):

    tournament_redirect_pattern_name = 'notifications-email'

    def default_send(self, p, default_send_queryset):
        return False

    def post(self, request, *args, **kwargs):
        people = Person.objects.filter(id__in=list(map(int, request.POST.getlist('recipients'))))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email_custom",
            "subject": request.POST['subject_line'],
            "body": request.POST['message_body'],
            "tournament": self.tournament.id,
            "send_to": [p.id for p in people],
        })

        self.add_sent_notification(len(people))
        return super().post(request, *args, **kwargs)


class TemplateEmailCreateView(BaseSelectPeopleEmailView):

    def get_initial(self):
        initial = super().get_initial()
        initial['subject_line'] = self.tournament.pref(self.subject_template)
        initial['message_body'] = self.tournament.pref(self.message_template)

        return initial

    def post(self, request, *args, **kwargs):
        self.tournament.preferences[self.subject_template] = request.POST['subject_line']
        self.tournament.preferences[self.message_template] = request.POST['message_body']
        email_recipients = list(map(int, request.POST.getlist('recipients')))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email",
            "message": self.event,
            "extra": self.get_extra(),
            "send_to": email_recipients,
            "subject": request.POST['subject_line'],
            "body": request.POST['message_body'],
        })

        self.add_sent_notification(len(email_recipients))
        return super().post(request, *args, **kwargs)


class TournamentTemplateEmailCreateView(TemplateEmailCreateView):

    def get_default_send_queryset(self):
        return super().get_default_send_queryset().exclude(
            sentmessage__notification__event=self.event, sentmessage__notification__tournament=self.tournament)

    def get_extra(self):
        extra = {'tournament_id': self.tournament.id}
        return extra


class RoundTemplateEmailCreateView(TemplateEmailCreateView, RoundMixin):

    def get_default_send_queryset(self):
        return super().get_default_send_queryset().exclude(
            sentmessage__notification__event=self.event, sentmessage__notification__round=self.round)

    def get_extra(self):
        extra = {'round_id': self.round.id}
        return extra
