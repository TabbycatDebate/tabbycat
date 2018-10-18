from smtplib import SMTPException

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic.edit import FormView

from participants.models import Person
from tournaments.mixins import TournamentMixin
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
    page_title = gettext_lazy("Email Participants")
    page_emoji = '📤'

    form_class = BasicEmailForm

    def get_queryset(self):
        queryset_filter = Q(speaker__team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)
        if self.tournament.pref('share_adjs'):
            queryset_filter |= Q(adjudicator__tournament__isnull=True)

        return Person.objects.filter(queryset_filter).select_related('speaker', 'adjudicator', 'speaker__team')

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key='name')

        table.add_column({'key': 'send', 'title': _("Send to")}, [{
            'component': 'check-cell',
            'checked': False,
            'id': p.id,
            'name': 'recipients',
            'value': p.id
        } for p in self.get_queryset()])

        table.add_column({'key': 'name', 'tooltip': _("Participant"), 'icon': 'user'}, [{
            'text': p.name,
            'tooltip': p.email,
            'class': 'no-wrap' if len(p.name) < 20 else ''
        } for p in self.get_queryset()])

        table.add_column({'key': 'role', 'title': _("Role")}, [{
            'text': _("Adj") if hasattr(p, 'adjudicator') else _("Spk")
        } for p in self.get_queryset()])

        return table


class CustomEmailCreateView(BaseSelectPeopleEmailView):
    template_name = "email_participants.html"

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('notifications-email', self.tournament)

    def post(self, request, *args, **kwargs):
        people = Person.objects.filter(id__in=request.POST.getlist('recipients'))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email_custom",
            "subject": request.POST['subject_line'],
            "message": request.POST['message_body'],
            "tournament": self.tournament.id,
            "send_to": [(p.id, p.email) for p in people]
        })

        return super().post(request, *args, **kwargs)
