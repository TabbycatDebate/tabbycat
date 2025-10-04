import base64
import logging
import zlib
from decimal import Decimal

import requests
import stripe
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms import SimpleArrayField
from django.core.cache import cache
from django.db.models import Count, Prefetch, Q, Sum
from django.forms import HiddenInput, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, FormView
from formtools.wizard.views import SessionWizardView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from participants.emoji import EMOJI_NAMES
from participants.models import Adjudicator, Coach, Person, Speaker, Team, TournamentInstitution
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from users.permissions import Permission
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import ModelFormSetView, VueTableTemplateView

from .forms import (AdjudicatorForm, CreatePaymentForm, FinishPayPalIntegrationForm, InstitutionCoachForm,
    ParticipantAllocationForm, PayPalCaptureOrderForm, PriceItemForm, SpeakerForm, TeamForm, TournamentInstitutionForm)
from .models import Discount, Invitation, Invoice, InvoicePayment, LineItem, Payment, PaymentConnection, PriceItem, Question
from .payment_utils import add_item, complete_paypal_order, generate_paypal_order, get_application_fee
from .types import Currency
from .utils import populate_invitation_url_keys

logger = logging.getLogger(__name__)


class CustomQuestionFormMixin:

    def get_form_kwargs(self, step=None):
        if step is not None:
            kwargs = super().get_form_kwargs(step)
        else:
            kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs


class InstitutionalRegistrationMixin:

    def get_institution(self):
        ti = TournamentInstitution.objects.filter(tournament=self.tournament, coach__url_key=self.kwargs['url_key']).select_related('institution')
        return get_object_or_404(ti).institution

    @property
    def institution(self):
        if not hasattr(self, '_institution'):
            self._institution = self.get_institution()
        return self._institution

    def get_form_kwargs(self, step=None):
        if step is not None:
            kwargs = super().get_form_kwargs(step)
        else:
            kwargs = super().get_form_kwargs()
        kwargs['institution'] = self.institution
        return kwargs

    def get_success_url(self):
        return reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': self.kwargs['url_key']})


class CreateInstitutionFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, SessionWizardView):
    form_list = [
        ('institution', TournamentInstitutionForm),
        ('coach', InstitutionCoachForm),
    ]
    template_name = 'institution_registration_form.html'
    page_emoji = '🏫'
    page_title = gettext_lazy("Register Institution")

    public_page_preference = 'institution_registration'
    action_log_type = ActionLogEntry.ActionType.INSTITUTION_REGISTER

    def get_success_url(self, coach):
        return reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': coach.url_key})

    def done(self, form_list, form_dict, **kwargs):
        t_inst = form_dict['institution'].save()
        self.object = t_inst

        coach_form = form_dict['coach']
        coach_form.instance.tournament_institution = t_inst
        coach = coach_form.save()

        invitations = [
            Invitation(tournament=self.tournament, institution=t_inst.institution, for_content_type=ContentType.objects.get_for_model(Adjudicator)),
            Invitation(tournament=self.tournament, institution=t_inst.institution, for_content_type=ContentType.objects.get_for_model(Team)),
        ]
        populate_invitation_url_keys(invitations, self.tournament)
        Invitation.objects.bulk_create(invitations)

        messages.success(self.request, _("Your institution %s has been registered!") % t_inst.institution.name)
        self.log_action()
        return HttpResponseRedirect(self.get_success_url(coach))


class BaseCreateTeamFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, SessionWizardView):
    form_list = [
        ('team', TeamForm),
        ('speaker', modelformset_factory(Speaker, form=SpeakerForm, extra=0)),
    ]
    template_name = 'team_registration_form.html'
    page_emoji = '👯'

    public_page_preference = 'open_team_registration'
    action_log_type = ActionLogEntry.ActionType.TEAM_REGISTER

    REFERENCE_GENERATORS = {
        'user': '_custom_reference',
        'alphabetical': '_alphabetical_reference',
        'numerical': '_numerical_reference',
        'initials': '_initials_reference',
    }

    CODE_NAME_GENERATORS = {
        'user': '_custom_code_name',
        'emoji': '_emoji_code_name',
        'last_names': '_last_names_code_name',
    }

    def get_template_names(self):
        if self.steps.current != 'speaker':
            return 'wizard_registration_form.html'
        return 'team_wizard_speakers.html'

    def get_page_title(self):
        match self.steps.current:
            case 'team':
                return _("Register Team")
            case 'speaker':
                return ngettext('Register Speaker', 'Register Speakers', self.tournament.pref('speakers_in_team'))
        return ''

    def get_team_form(self):
        form = self.get_form(
            self.steps.first,
            data=self.storage.get_step_data(self.steps.first),
        )
        team = form.instance
        team.tournament = self.tournament
        team.institution = self.institution
        team.reference = getattr(self, self.REFERENCE_GENERATORS[self.tournament.pref('team_name_generator')])(team, [])
        return form

    def get_page_subtitle(self):
        if self.steps.current == 'team' and getattr(self, 'institution', None) is not None:
            return _("from %s") % self.institution.name
        elif self.steps.current == 'speaker':
            team_form = self.get_team_form()
            if team_form.is_valid():
                return _("for %s") % team_form.instance._construct_short_name()
        return ''

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'speaker':
            kwargs.update({'queryset': self.get_speaker_queryset(), 'form_kwargs': {'team': self.get_team_form().instance}})
            kwargs.pop('tournament')
        return kwargs

    def get_speaker_queryset(self):
        return Speaker.objects.none()

    def get_success_url(self):
        return reverse_tournament('tournament-public-index', self.tournament)

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)

        if step == 'speaker':
            form.extra = self.tournament.pref('speakers_in_team')
            form.max_num = self.tournament.pref('speakers_in_team')
        return form

    def populate_cart_object(self, cart_item):
        cart_item.team = self.object

    def add_to_cart(self, team, speakers):
        items = self.tournament.priceitem_set.filter(active=True, item_type__in=[PriceItem.ItemType.PARTICIPANT, PriceItem.ItemType.TEAM, PriceItem.ItemType.SPEAKER])

        cart_items = [
            ci for ci in
            [
                add_item(items, PriceItem.ItemType.PARTICIPANT, len(speakers)),
                add_item(items, PriceItem.ItemType.TEAM, 1),
                add_item(items, PriceItem.ItemType.SPEAKER, len(speakers)),
            ]
            if ci is not None and ci.quantity
        ]
        for ci in cart_items:
            self.populate_cart_object(ci)

        LineItem.objects.bulk_create(cart_items)

    def done(self, form_list, form_dict, **kwargs):
        team = form_dict['team'].save()
        if self.tournament.pref('team_name_generator') != 'user':
            reference = getattr(self, self.REFERENCE_GENERATORS[self.tournament.pref('team_name_generator')])(form_dict['team'].instance, form_dict['speaker'])
            form_dict['team'].instance.reference = reference

        form_dict['team'].instance.code_name = getattr(self, self.CODE_NAME_GENERATORS[self.tournament.pref('code_name_generator')])(form_dict['team'].instance, form_dict['speaker'])
        team.save()
        self.object = team

        for speaker in form_dict['speaker']:
            speaker.team = team
        self.speakers = form_dict['speaker'].save()

        if len(self.speakers) < self.tournament.pref('speakers_in_team'):
            invitation = Invitation(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Speaker), team=team)
            populate_invitation_url_keys([invitation], self.tournament)
            invitation.save()

            invite_url = self.request.build_absolute_uri(
                reverse_tournament('reg-create-speaker', self.tournament, kwargs={'pk': team.pk}) + '?key=%s' % invitation.url_key,
                # replace with query={'key': invitation.url_key} in Django 5.2
            )
            messages.warning(self.request, ngettext(
                "Your team only has %(num)d speaker! Invite the other speakers to register using this link: <a href='%(link)s'>%(link)s</a>",
                "Your team only has %(num)d speakers! Invite the other speakers to register using this link: <a href='%(link)s'>%(link)s</a>",
                len(self.speakers),
            ) % {'num': len(self.speakers), 'link': invite_url})

        self.add_to_cart(team, form_dict['speaker'])

        messages.success(self.request, _("Your team %s has been registered!") % team.short_name)
        self.log_action()
        return HttpResponseRedirect(self.get_success_url())

    @staticmethod
    def _alphabetical_reference(team, speakers=None):
        teams = team.tournament.team_set.filter(institution=team.institution, reference__regex=r"^[A-Z]+$").values_list('reference', flat=True)
        team_numbers = []
        for existing_team in teams:
            n = 0
            for char in existing_team:
                n = n*26 + (ord(char) - 64)
            team_numbers.append(n)

        ch = ''
        mx = max(team_numbers, default=0) + 1
        while mx > 0:
            ch = chr(mx % 26 + 64) + ch
            mx //= 26

        return ch

    @staticmethod
    def _numerical_reference(team, speakers=None):
        teams = team.tournament.team_set.filter(institution=team.institution, reference__regex=r"^\d+$").values_list('reference', flat=True)
        team_numbers = [int(t) for t in teams]
        return str(max(team_numbers) + 1)

    @staticmethod
    def _initials_reference(team, speakers):
        return "".join(s.instance.last_name[0] for s in speakers)

    @staticmethod
    def _custom_reference(team, speakers=None):
        return team.reference

    @staticmethod
    def _custom_code_name(team, speakers=None):
        return team.code_name

    @staticmethod
    def _emoji_code_name(team, speakers=None):
        return EMOJI_NAMES[team.emoji]

    @staticmethod
    def _last_names_code_name(team, speakers=None):
        return ' & '.join(s.instance.last_name for s in speakers if s.instance.last_name is not None)


class PublicCreateTeamFormView(BaseCreateTeamFormView):

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('team-key') or self.request.POST.get('speaker-0-key')

    @property
    def institution(self):
        invitation = Invitation.objects.select_related('institution').filter(
            tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team), url_key=self.key).first()
        return getattr(invitation, 'institution', None)

    def is_page_enabled(self, tournament):
        if self.key:
            return (
                tournament.pref('institution_participant_registration') and
                Invitation.objects.filter(tournament=tournament, for_content_type=ContentType.objects.get_for_model(Team), url_key=self.key).count() == 1
            )
        return super().is_page_enabled(tournament)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs['key'] = self.key
        if step == 'speaker':
            kwargs.pop('key')
            kwargs['form_kwargs']['key'] = self.key
        else:
            kwargs['institution'] = self.institution
        return kwargs


class BaseCreateAdjudicatorFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, FormView):
    form_class = AdjudicatorForm
    template_name = 'adjudicator_registration_form.html'
    page_emoji = '👂'
    page_title = gettext_lazy("Register Adjudicator")

    public_page_preference = 'open_adj_registration'
    action_log_type = ActionLogEntry.ActionType.ADJUDICATOR_REGISTER

    def get_page_subtitle(self):
        if getattr(self, 'institution', None) is not None:
            return _("from %s") % self.institution.name
        return ''

    def get_success_url(self):
        return reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': self.object.url_key})

    def form_valid(self, form):
        self.object = form.save()
        self.add_to_cart(self.object)
        messages.success(self.request, _("You have been registered as an adjudicator!"))
        return super().form_valid(form)

    def populate_cart_object(self, cart_item, adjudicator):
        cart_item.person = adjudicator

    def add_to_cart(self, adjudicator):
        items = self.tournament.priceitem_set.filter(active=True, item_type__in=[PriceItem.ItemType.PARTICIPANT, PriceItem.ItemType.ADJUDICATOR])

        cart_items = [
            ci for ci in
            [
                add_item(items, PriceItem.ItemType.PARTICIPANT, 1),
                add_item(items, PriceItem.ItemType.ADJUDICATOR, 1),
            ]
            if ci is not None
        ]
        for ci in cart_items:
            self.populate_cart_object(ci, adjudicator)

        LineItem.objects.bulk_create(cart_items)


class PublicCreateAdjudicatorFormView(BaseCreateAdjudicatorFormView):

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('key')

    @property
    def institution(self):
        invitation = Invitation.objects.select_related('institution').filter(
            tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Adjudicator), url_key=self.key).first()
        return getattr(invitation, 'institution', None)

    def is_page_enabled(self, tournament):
        if self.key:
            return (
                tournament.pref('institution_participant_registration') and
                Invitation.objects.filter(tournament=tournament, for_content_type=ContentType.objects.get_for_model(Adjudicator), url_key=self.key).count() == 1
            )
        return super().is_page_enabled(tournament)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        invitation = Invitation.objects.select_related('institution').filter(
            tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Adjudicator), url_key=self.key).first()
        if invitation:
            kwargs['institution'] = invitation.institution
            kwargs['key'] = self.key
        return kwargs


class CreateSpeakerFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, FormView):
    form_class = SpeakerForm
    template_name = 'adjudicator_registration_form.html'
    page_emoji = '👄'
    page_title = gettext_lazy("Register Speaker")
    action_log_type = ActionLogEntry.ActionType.SPEAKER_REGISTER

    @property
    def team(self):
        return self.tournament.team_set.get(pk=self.kwargs['pk'])

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('key')

    def get_page_subtitle(self):
        return "for %s" % self.team.short_name

    def is_page_enabled(self, tournament):
        if self.key:
            team = tournament.team_set.prefetch_related('speaker_set').filter(pk=self.kwargs['pk']).first()
            return (
                tournament.pref('institution_participant_registration') and
                Invitation.objects.filter(tournament=tournament, for_content_type=ContentType.objects.get_for_model(Speaker), team=team, url_key=self.key).count() == 1 and
                team.speaker_set.count() < tournament.pref('speakers_in_team')
            )
        return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['team'] = self.team
        kwargs['key'] = self.key
        return kwargs

    def get_success_url(self):
        return reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': self.object.url_key})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _("You have been registered as a speaker!"))

        team = self.object.team
        speakers = team.speaker_set.all()
        if self.tournament.pref('team_name_generator') == 'initials':
            team.reference = BaseCreateTeamFormView._initials_reference(team, speakers)
        if self.tournament.pref('code_name_generator') == 'last_names':
            team.code_name = BaseCreateTeamFormView._last_names_code_name(team, speakers)
        team.save()
        return super().form_valid(form)

    def populate_cart_object(self, cart_item, speaker):
        if speaker.team.institution is not None:
            if self.tournament.pref('inst_billing_standard') == 'active_participants':
                cart_item.institution = speaker.team.institution
        else:
            cart_item.team = speaker.team
            cart_item.person = speaker

    def add_to_cart(self, speaker):
        items = self.tournament.priceitem_set.filter(active=True, item_type__in=[PriceItem.ItemType.PARTICIPANT, PriceItem.ItemType.SPEAKER])

        cart_items = [
            ci for ci in
            [
                add_item(items, PriceItem.ItemType.PARTICIPANT, 1),
                add_item(items, PriceItem.ItemType.SPEAKER, 1),
            ]
            if ci is not None
        ]
        for ci in cart_items:
            self.populate_cart_object(ci, speaker)

        LineItem.objects.bulk_create(cart_items)


class InstitutionalLandingPageView(TournamentMixin, InstitutionalRegistrationMixin, VueTableTemplateView):

    template_name = 'coach_private_url.html'

    def get_adj_table(self):
        adjudicators = self.tournament.adjudicator_set.filter(institution=self.institution)

        table = TabbycatTableBuilder(view=self, title=_('Adjudicators'), sort_key='name')
        table.add_adjudicator_columns(adjudicators, show_institutions=False, show_metadata=False)

        return table

    def get_team_table(self):
        teams = self.tournament.team_set.filter(institution=self.institution)
        table = TabbycatTableBuilder(view=self, title=_('Teams'), sort_key='name')
        table.add_team_columns(teams)

        return table

    def get_tables(self):
        return [self.get_adj_table(), self.get_team_table()]

    def get_context_data(self, **kwargs):
        kwargs["coach"] = get_object_or_404(Coach, tournament_institution__tournament=self.tournament, url_key=kwargs['url_key'])
        kwargs["institution"] = self.institution

        invitations = Invitation.objects.filter(tournament=self.tournament, institution=self.institution).select_related('for_content_type')
        for invitation in invitations:
            kwargs['%s_invitation_link' % invitation.for_content_type.model] = self.request.build_absolute_uri(
                reverse_tournament('reg-create-%s' % invitation.for_content_type.model, self.tournament) + '?key=%s' % invitation.url_key,
                # replace with query={'key': invitation.url_key} in Django 5.2
            )
        return super().get_context_data(**kwargs)


class InstitutionalCreateTeamFormView(InstitutionalRegistrationMixin, BaseCreateTeamFormView):

    public_page_preference = 'institution_participant_registration'

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'speaker':
            kwargs.pop('institution')
        return kwargs

    def populate_cart_object(self, cart_item):
        cart_item.institution = self.institution

    def add_to_cart(self, team, speakers):
        if self.tournament.pref('inst_billing_standard') == 'active_participants':
            return super().add_to_cart(team, speakers)


class InstitutionalCreateAdjudicatorFormView(InstitutionalRegistrationMixin, BaseCreateAdjudicatorFormView):
    public_page_preference = 'institution_participant_registration'

    def get_page_subtitle(self):
        return _("from %s") % self.institution.name

    def populate_cart_object(self, cart_item, adjudicator):
        cart_item.team = self.institution

    def add_to_cart(self, adjudicator):
        if self.tournament.pref('inst_billing_standard') == 'active_participants':
            return super().add_to_cart(adjudicator)


def handle_question_columns(table: TabbycatTableBuilder, objects, questions=None, suffix=0) -> None:
    if questions is None:
        questions = table.tournament.question_set.filter(for_content_type=ContentType.objects.get_for_model(objects.model)).order_by('seq')
    question_columns = {q: [] for q in questions}

    for obj in objects:
        obj_answers = {answer.question: answer.answer for answer in obj.answers.all()}
        for question, answers in question_columns.items():
            answers.append(obj_answers.get(question, ''))

    for question, answers in question_columns.items():
        table.add_column({'key': f'cq-{question.pk}-{suffix}', 'title': question.name}, answers)


class InstitutionRegistrationTableView(TournamentMixin, AdministratorMixin, VueTableTemplateView, FormView):
    form_class = ParticipantAllocationForm
    page_emoji = '🏫'
    page_title = gettext_lazy("Institutional Registration")
    template_name = 'answer_tables/institutions.html'

    view_permission = Permission.VIEW_REGISTRATION

    def get_table(self):
        t_institutions = self.tournament.tournamentinstitution_set.select_related('institution').prefetch_related(
            'answers__question',
        ).all()

        inst_team_count = {i.id: i.agg for i in self.tournament.tournamentinstitution_set.annotate(agg=Count('institution__team')).all()}
        inst_adj_count = {i.id: i.agg for i in self.tournament.tournamentinstitution_set.annotate(agg=Count('institution__adjudicator')).all()}

        form = self.get_form()

        table = TabbycatTableBuilder(view=self, title=_('Responses'), sort_key='name')
        table.add_column({'key': 'name', 'title': _("Name")}, [t_inst.institution.name for t_inst in t_institutions])
        table.add_column({'key': 'name', 'title': _("Coach")}, [{
            'text': (coach := t_inst.coach_set.first()).name,
            'link': reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': coach.url_key}),
        } for t_inst in t_institutions])
        if self.tournament.pref('reg_institution_slots'):
            table.add_column({'key': 'teams_requested', 'title': _("Teams Requested")}, [
                {'text': t_inst.teams_requested, 'sort': t_inst.teams_requested} for t_inst in t_institutions
            ])
            table.add_column({'key': 'teams_allocated', 'title': _("Teams Allocated")}, [
                {'text': str(form.get_teams_allocated_field(t_inst.institution)), 'sort': t_inst.teams_allocated} for t_inst in t_institutions
            ])

        if self.tournament.pref('institution_participant_registration'):
            table.add_column({'key': 'teams_registered', 'title': _("Teams Registered")}, [inst_team_count[t_inst.id] for t_inst in t_institutions])

        if self.tournament.pref('reg_institution_slots'):
            table.add_column({'key': 'adjudicators_requested', 'title': _("Adjudicators Requested")}, [
                {'text': t_inst.adjudicators_requested, 'sort': t_inst.adjudicators_requested} for t_inst in t_institutions
            ])
            table.add_column({'key': 'adjudicators_allocated', 'title': _("Adjudicators Allocated")}, [
                {'text': str(form.get_adjs_allocated_field(t_inst.institution)), 'sort': t_inst.adjudicators_allocated} for t_inst in t_institutions
            ])

        if self.tournament.pref('institution_participant_registration'):
            table.add_column({'key': 'adjudicators_registered', 'title': _("Adjudicators Registered")}, [inst_adj_count[t_inst.id] for t_inst in t_institutions])

        handle_question_columns(table, t_institutions)

        return table

    def get_success_url(self):
        return reverse_tournament('reg-institution-list', self.tournament)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Successfully modified institution allocations"))

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update(self.tournament.tournamentinstitution_set.aggregate(
            adjs_requested=Sum('adjudicators_requested'),
            adjs_allocated=Sum('adjudicators_allocated'),
            teams_requested=Sum('teams_requested'),
            teams_allocated=Sum('teams_allocated'),
        ))
        kwargs['adjs_registered'] = self.tournament.adjudicator_set.filter(institution__isnull=False, adj_core=False, independent=False).count()
        kwargs['teams_registered'] = self.tournament.team_set.filter(institution__isnull=False).count()
        return super().get_context_data(**kwargs)


class TeamRegistrationTableView(TournamentMixin, AdministratorMixin, VueTableTemplateView):
    page_emoji = '👯'
    page_title = gettext_lazy("Team Registration")
    template_name = 'answer_tables/teams.html'

    view_permission = Permission.VIEW_REGISTRATION

    def get_table(self):
        def get_speaker(team, i):
            try:
                return team.speakers[i]
            except IndexError:
                return Speaker()

        teams = self.tournament.team_set.select_related('institution').prefetch_related(
            'answers__question',
            Prefetch('speaker_set', queryset=Speaker.objects.prefetch_related('answers__question')),
        ).all()
        spk_questions = self.tournament.question_set.filter(for_content_type=ContentType.objects.get_for_model(Speaker)).order_by('seq')

        table = TabbycatTableBuilder(view=self, title=_('Responses'), sort_key='team')
        table.add_team_columns(teams)

        handle_question_columns(table, teams)

        for i in range(self.tournament.pref('speakers_in_team')):
            table.add_column({'key': 'spk-%d' % i, 'title': _("Speaker %d") % (i+1,)}, [get_speaker(team, i).name for team in teams])
            table.add_column({'key': 'email-%d' % i, 'title': _("Email")}, [get_speaker(team, i).email for team in teams])

            handle_question_columns(table, [get_speaker(team, i) for team in teams], questions=spk_questions, suffix=i)

        return table


class AdjudicatorRegistrationTableView(TournamentMixin, AdministratorMixin, VueTableTemplateView):
    page_emoji = '👂'
    page_title = gettext_lazy("Adjudicator Registration")
    template_name = 'answer_tables/adjudicators.html'

    view_permission = Permission.VIEW_REGISTRATION

    def get_table(self):
        adjudicators = self.tournament.adjudicator_set.select_related('institution').prefetch_related('answers__question').all()

        table = TabbycatTableBuilder(view=self, title=_('Responses'), sort_key='name')
        table.add_adjudicator_columns(adjudicators, show_metadata=False)
        table.add_column({'key': 'email', 'title': _("Email")}, [adj.email for adj in adjudicators])

        handle_question_columns(table, adjudicators)

        return table


class CustomQuestionFormsetView(TournamentMixin, AdministratorMixin, ModelFormSetView):
    formset_model = Question
    formset_factory_kwargs = {
        'fields': ['tournament', 'for_content_type', 'name', 'text', 'help_text', 'answer_type', 'required', 'min_value', 'max_value', 'choices'],
        'field_classes': {'choices': SimpleArrayField},
        'widgets': {
            'tournament': HiddenInput,
            'for_content_type': HiddenInput,
        },
        'extra': 3,
    }
    question_model = None
    template_name = 'questions_edit.html'

    view_permission = True
    edit_permission = Permission.EDIT_QUESTIONS

    page_emoji = '❓'
    page_title = gettext_lazy("Custom Questions")

    def get_formset_kwargs(self):
        return {
            'initial': [{
                'tournament': self.tournament,
                'for_content_type': ContentType.objects.get_for_model(self.question_model),
            }] * 3,
        }

    def get_page_subtitle(self):
        return _("for %s") % self.question_model._meta.verbose_name_plural

    def get_formset_queryset(self):
        return super().get_formset_queryset().filter(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(self.question_model)).order_by('seq')

    def formset_valid(self, formset):
        self.instances = formset.save(commit=False)
        if self.instances:
            for i, question in enumerate(self.instances, start=1):
                question.tournament = self.tournament
                question.for_content_type = ContentType.objects.get_for_model(self.question_model)
                question.seq = i
                question.save()

            messages.success(self.request, _("Questions for %(model)s were successfully saved.") % {'model': self.question_model._meta.verbose_name_plural})
        else:
            messages.success(self.request, _("No changes were made to the questions."))

        if "add_more" in self.request.POST:
            return HttpResponseRedirect(self.request.path_info)
        return super().formset_valid(formset)

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament(self.success_url, self.tournament)


class BasePaymentsIndexView(TournamentMixin, VueTableTemplateView):
    page_emoji = '💰'
    page_title = gettext_lazy("Payment Status")

    def get_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Payment Summary"))
        return table


class AdminPaymentsIndexView(AdministratorMixin, BasePaymentsIndexView):
    template_name = 'answer_tables/payments.html'

    def get_inst_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Institution Payments"))
        return table

    def get_team_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Team Payments"))
        return table

    def get_adj_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Adjudicator Payments"))
        return table

    def get_tables(self):
        return [self.get_inst_table(), self.get_adj_table(), self.get_team_table()]


class CreateProductsView(TournamentMixin, AdministratorMixin, ModelFormSetView):
    template_name = 'products_edit.html'

    formset_model = PriceItem
    formset_factory_kwargs = {
        'fields': ('tournament', 'item_type', 'name', 'amount', 'active'),
        'extra': 2,
        'widgets': {
            'tournament': HiddenInput(),
        },
        'form': PriceItemForm,
    }

    url_name = 'reg-products-edit'
    success_url = 'reg-payments-admin-list'

    def get_formset_queryset(self):
        return super().get_formset_queryset().filter(tournament=self.tournament)

    def get_formset_kwargs(self):
        return {
            'initial': [{'tournament': self.tournament}] * self.formset_factory_kwargs['extra'],
        }

    def formset_valid(self, formset):
        items = formset.save(commit=False)

        stripe_connection = self.tournament.paymentconnection_set.filter(platform=PaymentConnection.Platform.STRIPE).first()

        for item, fields in formset.changed_objects:
            if stripe_connection:
                new_data = {
                    'name': item.name or item.get_item_type_display().capitalize(),
                }
                if 'amount' in fields:
                    new_price = stripe.Price.create(
                        product=item.stripe_product_id,
                        currency=item.currency.lower(),
                        unit_amount=item.amount * Currency[item.currency].minor_unit,
                        api_key=settings.STRIPE_PRIVATE_API_KEY,
                        stripe_account=stripe_connection.external_id,
                    )
                    new_data['default_price'] = new_price['id']
                    item.stripe_price_id = new_price['id']

                stripe.Product.modify(
                    item.stripe_product_id,
                    **new_data,
                    api_key=settings.STRIPE_PRIVATE_API_KEY,
                    stripe_account=stripe_connection.external_id,
                )
            item.save()

        for item in formset.new_objects:
            item.tournament = self.tournament  # Even with the tournament in the form, avoid it being changed
            item.currency = self.tournament.pref('billing_currency')

            if stripe_connection:
                stripe_product = stripe.Product.create(
                    name=item.name or item.get_item_type_display().capitalize(),
                    default_price_data={
                        'currency': item.currency.lower(),
                        'unit_amount': item.amount * Currency[item.currency].minor_unit,
                    },
                    api_key=settings.STRIPE_PRIVATE_API_KEY,
                    stripe_account=stripe_connection.external_id,
                )
                item.stripe_product_id = stripe_product['id']
                item.stripe_price_id = stripe_product['default_price']
            item.save()

        if items:
            message = ngettext("Saved item: %(list)s",
                "Saved items: %(list)s",
                len(items),
            ) % {'list': ", ".join(item.name or item.get_item_type_display().capitalize() for item in items)}
            messages.success(self.request, message)
        else:
            messages.success(self.request, _("No changes were made to the items."))
        if "add_more" in self.request.POST:
            return redirect_tournament(self.url_name, self.tournament)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament(self.success_url, self.tournament)


class PaymentConnectionView(TournamentMixin, AdministratorMixin, TemplateView):
    template_name = 'payment_connections.html'

    def get_context_data(self, **kwargs):
        kwargs['has_stripe_connection'] = self.tournament.paymentconnection_set.filter(platform=PaymentConnection.Platform.STRIPE).exists()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        match request.POST.get('platform'):
            case 'stripe':
                return self.connect_stripe()
            case 'paypal':
                return self.connect_paypal()

    def connect_stripe(self):
        if not (connection := self.tournament.paymentconnection_set.filter(platform=PaymentConnection.Platform.STRIPE).first()):
            account = stripe.Account.create(api_key=settings.STRIPE_PRIVATE_API_KEY)
            connection = PaymentConnection(tournament=self.tournament, platform=PaymentConnection.Platform.STRIPE, external_id=account['id'], status=PaymentConnection.Status.PENDING)
            connection.save()

        account_link = stripe.AccountLink.create(
            api_key=settings.STRIPE_PRIVATE_API_KEY,
            account=connection.external_id,
            refresh_url=self.request.build_absolute_uri(reverse_tournament('stripe-connect-refresh', self.tournament)),
            return_url=self.request.build_absolute_uri(reverse_tournament('stripe-connect-return', self.tournament)),
            type="account_onboarding",
        )
        return HttpResponseRedirect(account_link['url'])

    def connect_paypal(self):
        if not (connection := self.tournament.paymentconnection_set.filter(platform=PaymentConnection.Platform.PAYPAL).first()):
            connection = PaymentConnection(
                tournament=self.tournament,
                platform=PaymentConnection.Platform.PAYPAL,
                external_id=f'temp_pp_{self.tournament.id}',
                status=PaymentConnection.Status.PENDING,
            )
            connection.save()

        req = requests.post('https://api-m.sandbox.paypal.com/v2/customer/partner-referrals', headers={'Authorization': 'Bearer x'}, json={
            "tracking_id": str(connection.id),
            "operations": [{
                "operation": "API_INTEGRATION",
                "api_integration_preference": {
                    "rest_api_integration": {
                        "integration_method": "PAYPAL",
                        "integration_type": "THIRD_PARTY",
                        "third_party_details": {
                            "features": [
                                "PAYMENT",
                                "REFUND",
                            ],
                        },
                    },
                },
            }],
            "products": [
                "EXPRESS_CHECKOUT",
            ],
            "legal_consents": [{
                "type": "SHARE_DATA_CONSENT",
                "granted": True,
            }],
            "partner_config_override": {
                'return_url': self.request.build_absolute_uri(reverse_tournament('paypal-connect-return', self.tournament)),
            },
        })
        return HttpResponseRedirect(next(link['url'] for link in req.json()['links'] if link['rel'] == 'action_url'))


class StripeAccountRefreshView(TournamentMixin, AdministratorMixin, View):
    def get(self, request, *args, **kwargs):
        messages.error(request, _("Your Stripe could not be linked. Please try again."))
        return HttpResponseRedirect(reverse_tournament('reg-payments-connect', self.tournament))


class StripeAccountReturnView(TournamentMixin, AdministratorMixin, View):
    def get(self, request, *args, **kwargs):
        messages.success(request, _("Your Stripe account has been linked"))
        return HttpResponseRedirect(reverse_tournament('reg-payments-admin-list', self.tournament))


class PayPalConnectReturnView(TournamentMixin, AdministratorMixin, FormView):
    form_class = FinishPayPalIntegrationForm

    def get_initial(self):
        initial = super().get_initial()
        initial['tracking_id'] = self.request.GET.get('merchantId')
        initial['merchant_id'] = self.request.GET.get('merchantIdInPayPal')
        return initial

    def get_success_url(self):
        return reverse_tournament('reg-payments-admin-list', self.tournament)

    def form_valid(self, form):
        connection = PaymentConnection.objects.get(platform=PaymentConnection.Platform.PAYPAL, id=form.cleaned_data['tracking_id'])
        connection.status = PaymentConnection.Status.CONNECTED
        connection.external_id = form.cleaned_data['merchant_id']
        connection.save()

        messages.success(self.request, _("Your PayPal account has been linked"))
        return super.form_valid(form)


class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        event = None
        account = request.headers['STRIPE_ACCOUNT']

        try:
            event = stripe.Webhook.construct_event(
                request.body,
                request.headers['STRIPE_SIGNATURE'],
                settings.STRIPE_WEBHOOK_SECRET,
                api_key=settings.STRIPE_PRIVATE_API_KEY,
                stripe_account=account,
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Handle the event
        match event.type:
            case 'account.updated':
                connections = PaymentConnection.objects.filter(platform=PaymentConnection.Platform.STRIPE, external_id=event.data.object['id'])
                if len(event.data.object['requirements']['past_due']) > 1:
                    connections.update(status=PaymentConnection.Status.DISCONNECTED)
                else:
                    connections.update(status=PaymentConnection.Status.CONNECTED)
            case 'checkout.session.completed':
                pass
            case 'checkout.session.expired':
                pass
            case _:
                print('Unhandled event type {}'.format(event['type']))

        return HttpResponse(status=200)


class PayPalWebhookView(View):
    def post(self, request, *args, **kwargs):
        # data = request.data

        if not PayPalWebhookView.verify_signature(request):
            return HttpResponse(status=400)

        match request.data.get("event_type"):
            case 'MERCHANT.ONBOARDING.COMPLETED':
                self.handle_onboarding_completed(request.data)
            case 'MERCHANT.PARTNER-CONSENT.REVOKED':
                pass

        return HttpResponse(status=200)

    @staticmethod
    def get_certificate(url):
        return cache.get_or_set(url, requests.get(url).text)

    @staticmethod
    def verify_signature(request):
        # Create the validation message
        transmission_id = request.headers.get("paypal-transmission-id")
        timestamp = request.headers.get("paypal-transmission-time")
        crc = zlib.crc32(request.body)
        message = f"{transmission_id}|{timestamp}|{settings.PAYPAL_WEBHOOK_ID}|{crc}"

        # Decode the base64-encoded signature from the header
        signature = base64.b64decode(request.headers.get("paypal-transmission-sig"))

        # Load the certificate and extract the public key
        certificate = PayPalWebhookView.get_certificate(request.headers.get("paypal-cert-url"))
        cert = x509.load_pem_x509_certificate(certificate.encode("utf-8"), default_backend())
        public_key = cert.public_key()

        # Validate the message using the signature
        try:
            public_key.verify(signature, message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            # Validation failed
            return False

    def handle_onboarding_completed(self, data):
        connection = PaymentConnection.objects.get(platform=PaymentConnection.Platform.PAYPAL, external_id=data['resource']['merchant_id'])
        connection.status = PaymentConnection.Status.CONNECTED
        connection.save()


class CreateInvoiceView(TournamentMixin, AdministratorMixin, CreateView):
    pass


class BaseInvoiceView(TournamentMixin, VueTableTemplateView):

    def get_queryset(self):
        return self.tournament.invoice_set.prefetch_related('lineitem_set', 'linediscount_set__discount', 'invoicepayment_set__payment')

    @property
    def invoice(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['invoice_id'])

    def get_items_table(self):
        items = self.invoice.lineitem_set.all()

        table = TabbycatTableBuilder(view=self, title=_("Items"))
        table.add_column({'key': 'item', 'title': _("Item")}, [li.item.name for li in items])
        table.add_column({'key': 'quantity', 'title': _("Quantity")}, [li.quantity for li in items])
        table.add_column({'key': 'price', 'title': _("Price")}, [li.item.amount * li.quantity for li in items])
        return table

    def get_discounts_table(self):
        discounts = self.invoice.linediscount_set.all()

        table = TabbycatTableBuilder(view=self, title=_("Discounts"))
        table.add_column({'key': 'note', 'title': _("Note")}, [d.note for d in discounts])
        table.add_column({'key': 'amount', 'title': _("Amount")}, [d.amount for d in discounts])
        return table

    def get_payments_table(self):
        payments = self.invoice.invoicepayment_set.all()

        table = TabbycatTableBuilder(view=self, title=_("Payments"))
        table.add_column({'key': 'timestamp', 'title': _("Date")}, [p.payment.timestamp for p in payments])
        table.add_column({'key': 'reference', 'title': _("Reference")}, [p.payment.reference for p in payments])
        table.add_column({'key': 'status', 'title': _("Status")}, [p.payment.get_status_display() for p in payments])
        table.add_column({'key': 'amount', 'title': _("Amount")}, [p.amount for p in payments])
        return table

    def get_tables(self):
        [self.get_items_table(), self.get_discounts_table(), self.get_payments_table()]


class InstitutionInvoiceView(InstitutionalRegistrationMixin, BaseInvoiceView):
    def get_queryset(self):
        return super().get_queryset().filter(institution=self.institution)


class PrivateUrlInvoiceView(BaseInvoiceView):
    def get_queryset(self):
        return super().get_queryset().filter(Q(team__speaker__url_key=self.kwargs['url_key']) | Q(person__url_key=self.kwargs['url_key']))


class AdminInvoiceView(AdministratorMixin, BaseInvoiceView):
    view_permission = Permission.VIEW_INVOICES


class BasePaymentView(TournamentMixin, VueTableTemplateView):
    def get_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Invoices"))
        return table


class AdminPaymentView(AdministratorMixin, BasePaymentView):
    view_permission = Permission.VIEW_PAYMENTS


class CreateDiscountView(TournamentMixin, AdministratorMixin, CreateView):
    model = Discount


class CreatePaymentView(TournamentMixin, AdministratorMixin, CreateView):
    model = Payment


class BaseBalanceSummaryView(TournamentMixin, VueTableTemplateView, FormView):
    template_name = 'account_balance.html'
    form_class = CreatePaymentForm

    tables_orientation = 'rows'

    def dispatch(self, request, *args, **kwargs):
        self.line_items = LineItem.objects.filter(item__tournament=self.tournament, **self.participant_kwargs)
        self.invoices = self.tournament.invoice_set.filter(**self.participant_kwargs)
        self.discounts = self.tournament.discount_set.filter(**self.participant_kwargs)
        self.payments = Payment.objects.filter(tournament=self.tournament, status=Payment.Status.COMPLETED, **self.participant_kwargs)
        self.line_items_total = sum([li.item.amount * li.quantity for li in self.line_items])
        self.amount_total = self.line_items_total - sum([d.amount for d in self.discounts]) - sum([p.amount for p in self.payments])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['total'] = self.amount_total
        return super().get_context_data(**kwargs)

    def get_invoices_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Invoices"))
        table.add_column({'key': 'name', 'title': _("ID")}, [i.pk for i in self.invoices])
        table.add_column({'key': 'status', 'title': _("Status")}, [i.get_status_display() for i in self.invoices])
        table.add_column({'key': 'total', 'title': _("Total")}, [i.amount for i in self.invoices])
        table.add_column({'key': 'due', 'title': _("Amount Due")}, [i.amount - i.amount_paid for i in self.invoices])
        return table

    def get_items_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Payment Summary"))
        table.add_column({'key': 'item', 'title': _("Item")}, [li.item.name or li.item.get_item_type_display().capitalize() for li in self.line_items])
        table.add_column({'key': 'quantity', 'title': _("Quantity")}, [li.quantity for li in self.line_items])
        table.add_column({'key': 'invoice', 'title': _("Invoice")}, [li.invoice_id for li in self.line_items])
        table.add_column({'key': 'price', 'title': _("Price")}, [li.item.amount * li.quantity for li in self.line_items])
        return table

    def get_discounts_table(self):
        table = TabbycatTableBuilder(view=self, title=_("Discounts"))
        table.add_column({'key': 'name', 'title': _("Name")}, [d.note for d in self.discounts])
        table.add_column({'key': 'amount', 'title': _("Amount")}, [d.amount for d in self.discounts])
        return table

    def get_tables(self):
        return [self.get_invoices_table(), self.get_items_table(), self.get_discounts_table()]

    def get_initial(self):
        initial = super().get_initial()
        initial['amount'] = self.amount_total
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['currency'] = Currency[self.tournament.pref('billing_currency')]
        kwargs['max_value'] = self.amount_total
        return kwargs

    def form_valid(self, form):
        currency = Currency[self.tournament.pref('billing_currency')]
        payment = Payment.objects.create(
            reference='',
            tournament=self.tournament,
            amount=form.cleaned_data['amount'],
            currency=currency,
            method=Payment.Method.OTHER,
            status=Payment.Status.PENDING,
            **self.participant_kwargs,
        )
        if new_invoice_items := self.line_items.filter(invoice=None):
            invoice = Invoice(
                amount=sum(ii.item.amount * ii.quantity for ii in new_invoice_items),
                currency=currency,
                tournament=self.tournament,
                status=Invoice.Status.OPEN,
                amount_paid=Decimal('0'),
                **self.participant_kwargs,
            )
            invoice.save()
            InvoicePayment.objects.create(payment=payment, invoice=invoice, amount=invoice.amount, currency=currency)
            new_invoice_items.update(invoice=invoice)

        payment_connections = {pc.platform: pc for pc in self.tournament.paymentconnection_set.filter(status=PaymentConnection.Status.CONNECTED)}
        if PaymentConnection.Platform.STRIPE in payment_connections:
            payment.method = Payment.Method.STRIPE
            payment.save()
            return self.create_stripe_checkout(payment_connections[PaymentConnection.Platform.STRIPE], form.cleaned_data['amount'], payment)
        if PaymentConnection.Platform.PAYPAL in payment_connections:
            payment.method = Payment.Method.PAYPAL
            payment.save()
            return self.create_paypal_checkout(payment_connections[PaymentConnection.Platform.PAYPAL], form.cleaned_data['amount'], payment)

    def create_stripe_checkout(self, connection, amount, payment):
        use_currency = Currency[self.tournament.pref('billing_currency')]
        discounts = []
        if amount < self.line_items_total:
            coupon = stripe.Coupon.create(
                name='For partial payment / discounts',
                amount_off=(self.line_items_total - amount) * use_currency.minor_unit,
                currency=self.tournament.pref('billing_currency'),
                max_redemptions=1,
                api_key=settings.STRIPE_PRIVATE_API_KEY,
                stripe_account=connection.external_id,
            )
            discounts.append({'coupon': coupon['id']})

        session = stripe.checkout.Session.create(
            success_url=self.request.build_absolute_uri(),
            line_items=[{"price": li.item.stripe_price_id, "quantity": li.quantity} for li in self.line_items],
            discounts=discounts,
            mode="payment",
            client_reference_id=payment.id,
            payment_intent_data={'application_fee_amount': int(get_application_fee(amount, use_currency) * use_currency.minor_unit)},
            api_key=settings.STRIPE_PRIVATE_API_KEY,
            stripe_account=connection.external_id,
        )
        return HttpResponseRedirect(session['url'])

    def create_paypal_checkout(self, connection, amount, payment):
        return JsonResponse(generate_paypal_order(connection, amount, self.line_items, payment))


class InstitutionBalanceSummaryView(BaseBalanceSummaryView):

    def get_t_institution(self):
        ti = TournamentInstitution.objects.filter(tournament=self.tournament, coach__url_key=self.kwargs['url_key']).select_related('institution')
        return get_object_or_404(ti)

    @property
    def institution(self):
        return self.get_t_institution().institution

    @property
    def participant_kwargs(self):
        return {'institution': self.institution}


class AdminInstitutionBalanceSummaryView(AdministratorMixin, BaseBalanceSummaryView):
    view_permission = Permission.VIEW_INVOICES

    @property
    def participant_kwargs(self):
        return {'institution': self.kwargs['pk']}


class AdminTeamBalanceSummaryView(AdministratorMixin, BaseBalanceSummaryView):
    view_permission = Permission.VIEW_INVOICES

    @property
    def participant_kwargs(self):
        return {'team': self.kwargs['pk']}


class AdminPersonBalanceSummaryView(AdministratorMixin, BaseBalanceSummaryView):
    view_permission = Permission.VIEW_INVOICES

    @property
    def participant_kwargs(self):
        return {'person': self.kwargs['pk']}


class PrivateUrlBalanceSummaryView(BaseBalanceSummaryView):
    @property
    def participant_kwargs(self):
        person = Person.objects.filter(url_key=self.kwargs['url_key']).select_related('speaker__team', 'adjudicator').get()
        if person.speaker is not None:
            return {'team': person.speaker.team}
        return {'person': person}


class PayPalCaptureOrderView(TournamentMixin, FormView):
    form_class = PayPalCaptureOrderForm

    def form_valid(self, form):
        connection = self.tournament.paymentconnection_set.filter(status=PaymentConnection.Status.CONNECTED, platform=PaymentConnection.Platform.STRIPE)
        return JsonResponse(complete_paypal_order(connection, form.cleaned_data['order_id']))
