from smtplib import SMTPException

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic.edit import FormView

from participants.models import Person, Speaker
from tournaments.mixins import RoundMixin, TournamentMixin
from utils.misc import reverse_round, reverse_tournament
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

    sort_key = 'role'

    def get_default_send_queryset(self):
        return self.get_queryset().filter(email__isnull=False).exclude(email__exact="")

    def get_queryset(self):
        """All the people from the tournament who could receive the message"""
        queryset_filter = Q(speaker__team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)
        if self.tournament.pref('share_adjs'):
            queryset_filter |= Q(adjudicator__tournament__isnull=True)

        return Person.objects.filter(queryset_filter).select_related('speaker', 'adjudicator', 'speaker__team')

    def default_send(self, p):
        """Whether the person should be emailed by default"""
        return p.id in [a.id for a in self.get_default_send_queryset()]

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key='name')

        table.add_column({'key': 'send', 'title': _("Send to")}, [{
            'component': 'check-cell',
            'checked': self.default_send(p),
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
    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('notifications-email', self.tournament)

    def default_send(self, p):
        return False

    def post(self, request, *args, **kwargs):
        people = Person.objects.filter(id__in=request.POST.getlist('recipients'))

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email_custom",
            "subject": request.POST['subject_line'],
            "message": request.POST['message_body'],
            "tournament": self.tournament.id,
            "send_to": [(p.id, p.email) for p in people]
        })

        messages.success(request, _("Emails have been queued for sending."))
        return super().post(request, *args, **kwargs)


class TemplateEmailCreateView(BaseSelectPeopleEmailView):

    def get_page_subtitle(self):
        return {
            "adj": _("Adjudicator Assignments"),
            "url": _("Private URLs"),
            "team_points": _("Team Standings"),
            "motion": _("Round Motions"),
            "team": _("Team Registration")
        }[self.event_type]

    def get(self, request, *args, **kwargs):
        if self.kwargs['event_type'] in self.allowed_email_types:
            self.event_type = self.kwargs['event_type']
        else:
            raise Http404(_("There is no email template with that name."))

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['subject_line'] = self.tournament.pref(self.event_type + "_email_subject")
        initial['message_body'] = self.tournament.pref(self.event_type + "_email_message")

        return initial

    def post(self, request, *args, **kwargs):
        self.event_type = self.kwargs['event_type']

        self.tournament.preferences[self.event_type + "_email_subject"] = request.POST['subject_line']
        self.tournament.preferences[self.event_type + "_email_message"] = request.POST['message_body']

        async_to_sync(get_channel_layer().send)("notifications", {
            "type": "email",
            "message": self.event_type,
            "extra": self.get_extra(),
            "send_to": list(map(int, request.POST.getlist('recipients')))
        })

        messages.success(request, _("Emails have been queued for sending."))
        return super().post(request, *args, **kwargs)


class TournamentTemplateEmailCreateView(TemplateEmailCreateView):
    allowed_email_types = ['url', 'team']

    def get_queryset(self):
        if self.event_type == 'team':
            return Speaker.objects.filter(team__tournament=self.tournament)
        else:
            return super().get_queryset()

    def get_extra(self):
        extra = {'tournament_id': self.tournament.id}
        if self.event_type == 'url':
            extra['url'] = self.request.build_absolute_uri(
                reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': '0'}))[:-2]
        return extra

    def get_success_url(self):
        return {
            'url': reverse_tournament('privateurls-list', self.tournament),
            'team': reverse_tournament('participants-list', self.tournament)
        }[self.event_type]


class RoundTemplateEmailCreateView(TemplateEmailCreateView, RoundMixin):
    allowed_email_types = ['adj', 'team_points', 'motion']

    def get_queryset(self):
        if self.event_type == 'adj':
            return self.round.active_adjudicators
        elif self.event_type == 'team_points':
            return Speaker.objects.filter(team__tournament=self.tournament)
        else:
            return super().get_queryset()

    def get_default_send_queryset(self):
        if self.event_type == 'team_points' or self.event_type == 'motion':
            return Speaker.objects.filter(
                team__round_availabilities__round=self.round,
                email__isnull=False
            ).exclude(email__exact="")
        else:
            return super().get_default_send_queryset()

    def get_extra(self):
        extra = {'tournament_id': self.tournament.id, 'round_id': self.round.id}
        if self.event_type == 'team_points':
            extra['url'] = self.request.build_absolute_uri(reverse_tournament('standings-public-teams-current', self.tournament))
        return extra

    def get_success_url(self):
        return {
            'adj': reverse_round('draw-display', self.round),
            'team_points': reverse_round('tournament-complete-round-check', self.round),
            'motion': reverse_round('draw-display', self.round)
        }[self.event_type]
