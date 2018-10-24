from smtplib import SMTPException

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.edit import FormView

from participants.models import Person
from tournaments.mixins import RoundMixin, TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import VueTableTemplateView

from .forms import BasicEmailForm, TestEmailForm


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


class BaseSelectPeopleEmailView(AdministratorMixin, TournamentMixin, VueTableTemplateView, FormView):
    template_name = "email_participants.html"
    page_title = gettext_lazy("Email Participants")
    page_emoji = '📤'

    form_class = BasicEmailForm

    def get_default_send_queryset(self):
        return self.get_queryset().filter(email__isnull=False).exclude(email__exact="")

    def get_queryset(self):
        """All the people from the tournament who could receive the message"""
        queryset_filter = Q(speaker__team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)
        if self.tournament.pref('share_adjs'):
            queryset_filter |= Q(adjudicator__tournament__isnull=True)

        return Person.objects.filter(queryset_filter).select_related('speaker', 'adjudicator')

    def default_send(self, p, default_send_queryset=None):
        """Whether the person should be emailed by default"""
        return p in default_send_queryset

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
            'type': 'adj' if mixed_participants and hasattr(p, 'adjudicator') else 'spk'
        } for p in queryset])

        table.add_column({'key': 'name', 'tooltip': _("Participant"), 'icon': 'user'}, [{
            'text': p.name,
            'class': 'no-wrap' if len(p.name) < 20 else ''
        } for p in queryset])

        table.add_column({'key': 'email', 'tooltip': _("Email Address"), 'icon': 'mail'}, [{
            'text': p.email if p.email else _("Not Provided"),
            'class': 'small' if p.email else 'small text-warning'
        } for p in queryset])

        return table


class RoleColumnMixin:
    """Mixin to have a column Adjudicator/Speaker for email"""

    def get_table(self, mixed_participants=True):
        table = super().get_table()

        table.add_column({'key': 'role', 'title': _("Role")}, [{
            'text': _("Adjudicator") if hasattr(p, 'adjudicator') else _("Speaker")
        } for p in self.get_queryset()])

        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'id': 'spk', 'name': _("Speakers")},
            {'id': 'adj', 'name': _("Adjudicators")}
        ]
        return context


class CustomEmailCreateView(RoleColumnMixin, BaseSelectPeopleEmailView):

    def get_success_url(self):
        return reverse_tournament('notifications-email', self.tournament)

    def default_send(self, p, default_send_queryset):
        return False

    def post(self, request, *args, **kwargs):
        people = Person.objects.filter(id__in=list(map(int, request.POST.getlist('recipients'))))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email_custom",
            "subject": request.POST['subject_line'],
            "message": request.POST['message_body'],
            "tournament": self.tournament.id,
            "send_to": [(p.id, p.email) for p in people]
        })

        messages.success(request, ngettext(
            "%(count)s email has been queued for sending.",
            "%(count)s emails have been queued for sending.",
            len(people)
        ) % {'count': len(people)})
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
            "body": request.POST['message_body']
        })

        messages.success(request, ngettext(
            "%(count)s email has been queued for sending.",
            "%(count)s emails have been queued for sending.",
            len(email_recipients)
        ) % {'count': len(email_recipients)})
        return super().post(request, *args, **kwargs)


class TournamentTemplateEmailCreateView(TemplateEmailCreateView):

    def get_extra(self):
        extra = {'tournament_id': self.tournament.id}
        return extra


class RoundTemplateEmailCreateView(TemplateEmailCreateView, RoundMixin):

    def get_extra(self):
        extra = {'round_id': self.round.id}
        return extra
