from typing import Sequence

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, Max, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.forms import HiddenInput, modelformset_factory, Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.edit import FormView
from formtools.wizard.views import SessionWizardView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from notifications.models import BulkNotification
from participants.emoji import EMOJI_NAMES
from participants.models import (
    Adjudicator,
    Coach,
    Institution,
    RegistrationStatus,
    Speaker,
    Team,
    TournamentInstitution,
)
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from users.permissions import Permission
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import ModelFormSetView, PostOnlyRedirectView, VueTableTemplateView

from .forms import (
    AdjudicatorForm,
    InstitutionCoachForm,
    InstitutionEditForm,
    ParticipantAllocationForm,
    SlotTransferRequestForm,
    SpeakerForm,
    TeamForm,
    TournamentInstitutionForm,
)
from .models import Invitation, Question, SlotTransferRequest
from .utils import add_confirm_button_column, add_slot_transfer_status_column, populate_invitation_url_keys


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
    action_log_content_object_attr = 'object'

    @property
    def key(self):
        return (
            self.request.GET.get('key') or self.request.POST.get('key') or
            self.request.POST.get('institution-key') or self.request.POST.get('coach-key')
        )

    def is_page_enabled(self, tournament):
        if self.key:
            return (
                Invitation.objects.filter(
                    tournament=tournament,
                    for_content_type=ContentType.objects.get_for_model(Institution),
                    url_key=self.key,
                ).exists()
            )
        return super().is_page_enabled(tournament)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if self.key:
            kwargs['key'] = self.key
        return kwargs

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

        if self.key:
            Invitation.objects.filter(
                tournament=self.tournament,
                for_content_type=ContentType.objects.get_for_model(Institution),
                url_key=self.key,
            ).delete()

        subject = self.tournament.pref('institution_registration_email_subject')
        body = self.tournament.pref('institution_registration_email_body')
        if subject and body and coach.email:
            landing_url = self.request.build_absolute_uri(
                reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': coach.url_key}),
            )
            async_to_sync(get_channel_layer().send)("notifications", {
                "type": "email",
                "message": BulkNotification.EventType.INSTITUTION_REG,
                "extra": {"tournament_id": self.tournament.pk, "url": landing_url},
                "send_to": [coach.pk],
                "subject": subject,
                "body": body,
            })

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
    action_log_content_object_attr = 'object'

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

    def done(self, form_list, form_dict, **kwargs):
        team = form_dict['team'].save()
        speaker_objs = [s.instance for s in form_dict['speaker']]
        if self.tournament.pref('team_name_generator') != 'user':
            reference = getattr(self, self.REFERENCE_GENERATORS[self.tournament.pref('team_name_generator')])(team, speaker_objs)
            team.reference = reference

        team.code_name = getattr(self, self.CODE_NAME_GENERATORS[self.tournament.pref('code_name_generator')])(team, speaker_objs)
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

        messages.success(self.request, _("Your team %s has been registered!") % team.short_name)
        self.log_action()
        return HttpResponseRedirect(self.get_success_url())

    @staticmethod
    def _alphabetical_reference(team, speakers=None):
        teams = Team.objects.all_with_unconfirmed.filter(tournament=team.tournament, institution=team.institution, reference__regex=r"^[A-Z]+$").values_list('reference', flat=True)
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
    def _numerical_reference(team, speakers: Sequence[Speaker]):
        teams = Team.objects.all_with_unconfirmed.filter(tournament=team.tournament, institution=team.institution, reference__regex=r"^\d+$").values_list('reference', flat=True)
        team_numbers = [int(t) for t in teams]
        return str(max(team_numbers) + 1)

    @staticmethod
    def _initials_reference(team, speakers: Sequence[Speaker]):
        return "".join(s.last_name[0] for s in speakers)

    @staticmethod
    def _custom_reference(team, speakers: Sequence[Speaker]):
        return team.reference

    @staticmethod
    def _custom_code_name(team, speakers: Sequence[Speaker]):
        return team.code_name

    @staticmethod
    def _emoji_code_name(team, speakers: Sequence[Speaker]):
        return EMOJI_NAMES[team.emoji]

    @staticmethod
    def _last_names_code_name(team, speakers: Sequence[Speaker]):
        return ' & '.join(s.last_name for s in speakers if s.last_name is not None)


class PublicCreateTeamFormView(BaseCreateTeamFormView):

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('team-key') or self.request.POST.get('speaker-0-key')

    def _get_team_invitation(self):
        if not getattr(self, '_team_invitation', None) and self.key:
            self._team_invitation = Invitation.objects.select_related('institution').filter(
                tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team), url_key=self.key,
            ).first()
        return getattr(self, '_team_invitation', None)

    @property
    def institution(self):
        invitation = self._get_team_invitation()
        return getattr(invitation, 'institution', None) if invitation else None

    def is_page_enabled(self, tournament):
        if not self.key:
            return super().is_page_enabled(tournament)
        invitation = Invitation.objects.select_related('institution').filter(
            tournament=tournament, for_content_type=ContentType.objects.get_for_model(Team), url_key=self.key,
        ).first()
        if not invitation or not tournament.pref('institution_participant_registration'):
            return False
        if invitation.institution_id is not None and tournament.pref('reg_institution_slots'):
            t_inst = TournamentInstitution.objects.filter(
                tournament=tournament, institution=invitation.institution,
            ).first()
            if not t_inst:
                return False
            team_count = Team.objects.all_with_unconfirmed.filter(
                tournament=tournament, institution=invitation.institution,
            ).count()
            if team_count >= t_inst.teams_allocated:
                return False
        return True

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs['key'] = self.key
        if step == 'speaker':
            kwargs.pop('key')
            kwargs['form_kwargs']['key'] = self.key
        else:
            kwargs['institution'] = self.institution
        return kwargs

    def done(self, form_list, form_dict, **kwargs):
        response = super().done(form_list, form_dict, **kwargs)
        invitation = self._get_team_invitation()
        if invitation is not None and invitation.institution_id is None:
            invitation.delete()
        return response


class BaseCreateAdjudicatorFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, FormView):
    form_class = AdjudicatorForm
    template_name = 'adjudicator_registration_form.html'
    page_emoji = '👂'
    page_title = gettext_lazy("Register Adjudicator")

    public_page_preference = 'open_adj_registration'
    action_log_type = ActionLogEntry.ActionType.ADJUDICATOR_REGISTER
    action_log_content_object_attr = 'object'

    def get_page_subtitle(self):
        if getattr(self, 'institution', None) is not None:
            return _("from %s") % self.institution.name
        return ''

    def get_success_url(self):
        return reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': self.object.url_key})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _("You have been registered as an adjudicator!"))
        return super().form_valid(form)


class PublicCreateAdjudicatorFormView(BaseCreateAdjudicatorFormView):

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('key')

    def _get_adj_invitation(self):
        if not getattr(self, '_adj_invitation', None) and self.key:
            self._adj_invitation = Invitation.objects.select_related('institution').filter(
                tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Adjudicator), url_key=self.key,
            ).first()
        return getattr(self, '_adj_invitation', None)

    @property
    def institution(self):
        invitation = self._get_adj_invitation()
        return getattr(invitation, 'institution', None) if invitation else None

    def is_page_enabled(self, tournament):
        if not self.key:
            return super().is_page_enabled(tournament)
        invitation = Invitation.objects.select_related('institution').filter(
            tournament=tournament, for_content_type=ContentType.objects.get_for_model(Adjudicator), url_key=self.key,
        ).first()
        if not invitation or not tournament.pref('institution_participant_registration'):
            return False
        if invitation.institution_id is not None and tournament.pref('reg_institution_slots'):
            t_inst = TournamentInstitution.objects.filter(
                tournament=tournament, institution=invitation.institution,
            ).first()
            if not t_inst:
                return False
            adj_count = Adjudicator.objects.all_with_unconfirmed.filter(
                tournament=tournament, institution=invitation.institution,
            ).count()
            if adj_count >= t_inst.adjudicators_allocated:
                return False
        return True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        invitation = self._get_adj_invitation()
        if invitation:
            kwargs['institution'] = invitation.institution
            kwargs['key'] = self.key
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        invitation = self._get_adj_invitation()
        if invitation is not None and invitation.institution_id is None:
            invitation.delete()
        return response


class CreateSpeakerFormView(LogActionMixin, PublicTournamentPageMixin, CustomQuestionFormMixin, FormView):
    form_class = SpeakerForm
    template_name = 'speaker_registration_form.html'
    page_emoji = '👄'
    page_title = gettext_lazy("Register Speaker")
    action_log_type = ActionLogEntry.ActionType.SPEAKER_REGISTER
    action_log_content_object_attr = 'object'

    @property
    def team(self):
        return Team.objects.all_with_unconfirmed.get(tournament=self.tournament, pk=self.kwargs['pk'])

    @property
    def key(self):
        return self.request.GET.get('key') or self.request.POST.get('key')

    def get_page_subtitle(self):
        return "for %s" % self.team.short_name

    def is_page_enabled(self, tournament):
        if self.key:
            team = Team.objects.all_with_unconfirmed.prefetch_related('speaker_set').filter(tournament=tournament, pk=self.kwargs['pk']).first()
            return (
                Invitation.objects.filter(tournament=tournament, for_content_type=ContentType.objects.get_for_model(Speaker), team=team, url_key=self.key).exists() and
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


class InstitutionalLandingPageView(TournamentMixin, InstitutionalRegistrationMixin, VueTableTemplateView):

    template_name = 'coach_private_url.html'

    def get_adj_table(self):
        adjudicators = Adjudicator.objects.all_with_unconfirmed.filter(tournament=self.tournament, institution=self.institution)

        table = TabbycatTableBuilder(view=self, title=_('Adjudicators'), sort_key='name')
        table.add_adjudicator_columns(adjudicators, show_institutions=False, show_metadata=False)

        return table

    def get_team_table(self):
        teams = Team.objects.all_with_unconfirmed.filter(tournament=self.tournament, institution=self.institution)
        table = TabbycatTableBuilder(view=self, title=_('Teams'), sort_key='name')
        table.add_team_columns(teams)

        return table

    def get_tables(self):
        return [self.get_adj_table(), self.get_team_table()]

    def get_context_data(self, **kwargs):
        coach = get_object_or_404(
            Coach.objects.select_related('tournament_institution').prefetch_related(
                'tournament_institution__answers__question',
                'answers__question',
            ),
            tournament_institution__tournament=self.tournament,
            url_key=kwargs['url_key'],
        )
        kwargs["coach"] = coach
        kwargs["institution"] = self.institution
        t_inst = coach.tournament_institution
        kwargs["tournament_institution"] = t_inst

        # Slot counts for this institution
        if self.tournament.pref('reg_institution_slots'):
            kwargs["teams_requested"] = t_inst.teams_requested
            kwargs["teams_allocated"] = t_inst.teams_allocated
            kwargs["adjudicators_requested"] = t_inst.adjudicators_requested
            kwargs["adjudicators_allocated"] = t_inst.adjudicators_allocated
        if self.tournament.pref('institution_participant_registration'):
            kwargs["teams_registered"] = Team.objects.all_with_unconfirmed.filter(
                tournament=self.tournament, institution=self.institution,
            ).count()
            kwargs["adjudicators_registered"] = Adjudicator.objects.all_with_unconfirmed.filter(
                tournament=self.tournament, institution=self.institution,
            ).count()

        # Form answers for review (ordered by question sequence)
        kwargs["institution_answers"] = list(
            t_inst.answers.select_related('question').order_by('question__seq'),
        )
        kwargs["coach_answers"] = list(
            coach.answers.select_related('question').order_by('question__seq'),
        )

        invitations = Invitation.objects.filter(tournament=self.tournament, institution=self.institution).select_related('for_content_type')
        for invitation in invitations:
            kwargs['%s_invitation_link' % invitation.for_content_type.model] = self.request.build_absolute_uri(
                reverse_tournament('reg-create-%s' % invitation.for_content_type.model, self.tournament) + '?key=%s' % invitation.url_key,
                # replace with query={'key': invitation.url_key} in Django 5.2
            )
        return super().get_context_data(**kwargs)


class AdminEditInstitutionFormView(TournamentMixin, AdministratorMixin, FormView):
    """Admin editing the answers of an institution (FormView with separate sections for institution and primary contact)."""

    form_class = InstitutionEditForm
    template_name = 'registration/institution_edit.html'
    page_emoji = '🏫'
    page_title = gettext_lazy("Edit institution registration")
    view_permission = Permission.VIEW_REGISTRATION
    edit_permission = Permission.VIEW_REGISTRATION

    def get_t_inst(self):
        return get_object_or_404(
            TournamentInstitution.objects.select_related('institution').prefetch_related(
                'answers__question',
                'coach_set__answers__question',
            ),
            tournament=self.tournament,
            pk=self.kwargs['pk'],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        kwargs['t_inst'] = self.get_t_inst()
        return kwargs

    def get_success_url(self):
        return reverse_tournament('reg-institution-list', self.tournament)

    def get_context_data(self, **kwargs):
        kwargs['t_inst'] = self.get_t_inst()
        kwargs['page_subtitle'] = kwargs['t_inst'].institution.name
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        t_inst = form.t_inst
        inst_form = form.institution_form
        coach_form = form.coach_form

        inst = t_inst.institution
        inst.name = inst_form.cleaned_data['name']
        inst.code = inst_form.cleaned_data['code']
        inst.region = inst_form.cleaned_data.get('region', None)
        inst.save()

        if 'teams_requested' in inst_form.fields:
            t_inst.teams_requested = inst_form.cleaned_data.get('teams_requested', 0)
            t_inst.adjudicators_requested = inst_form.cleaned_data.get('adjudicators_requested', 0)
        t_inst.save()

        inst_form.save_answers(t_inst, replace_existing=True)
        coach_form.save()

        messages.success(self.request, _("Institution %s updated.") % inst.name)
        return super().form_valid(form)


class CoachViewResponseFormView(PublicTournamentPageMixin, InstitutionalRegistrationMixin, FormView):
    # This form is read-only: coaches can view their institution and primary contact response but cannot edit.
    form_class = InstitutionEditForm
    template_name = 'registration/institution_view_response.html'
    page_emoji = '📋'
    page_title = gettext_lazy("Registration form response")

    def get_page_subtitle(self):
        return "for %s" % self.institution.name

    def is_page_enabled(self, tournament):
        return True

    def get_t_inst(self):
        return get_object_or_404(
            TournamentInstitution.objects.select_related('institution').prefetch_related(
                'answers__question',
                'coach_set__answers__question',
            ),
            tournament=self.tournament,
            coach__url_key=self.kwargs['url_key'],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('institution', None)
        kwargs['tournament'] = self.tournament
        kwargs['t_inst'] = self.get_t_inst()
        kwargs['read_only'] = True
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['t_inst'] = self.get_t_inst()
        kwargs['url_key'] = self.kwargs['url_key']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        return HttpResponse(status=403)


class SlotTransferRequestFormView(PublicTournamentPageMixin, InstitutionalRegistrationMixin, FormView):
    form_class = SlotTransferRequestForm
    template_name = 'slot_transfer_request_form.html'
    page_emoji = '↔'
    page_title = gettext_lazy("Transfer slots")

    def is_page_enabled(self, tournament):
        return tournament.pref('reg_institution_slots') and tournament.pref('reg_institution_slot_transfers')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        source_ti = TournamentInstitution.objects.get(
            tournament=self.tournament,
            institution=self.institution,
        )
        kwargs['source_tournament_institution'] = source_ti
        kwargs.pop('institution')
        return kwargs

    def get_success_url(self):
        return reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': self.kwargs['url_key']})

    def get_context_data(self, **kwargs):
        kwargs['url_key'] = self.kwargs['url_key']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Your slot transfer request has been submitted and is pending approval."))
        return super().form_valid(form)


class InstitutionalCreateTeamFormView(InstitutionalRegistrationMixin, BaseCreateTeamFormView):

    public_page_preference = 'institution_participant_registration'

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'speaker':
            kwargs.pop('institution')
        return kwargs


class InstitutionalCreateAdjudicatorFormView(InstitutionalRegistrationMixin, BaseCreateAdjudicatorFormView):
    public_page_preference = 'institution_participant_registration'


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
        table.add_column({'key': 'name', 'title': _("Name")}, [
            {'text': t_inst.institution.name, 'link': reverse_tournament('reg-institution-edit', self.tournament, kwargs={'pk': t_inst.pk})}
            for t_inst in t_institutions
        ])
        table.add_column({'key': 'code', 'title': _("Code")}, [t_inst.institution.code for t_inst in t_institutions])
        table.add_column({'key': 'coach', 'title': _("Coach")}, [{
            'text': (coach := t_inst.coach_set.first()).name,
            'link': reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': coach.url_key}),
        } for t_inst in t_institutions])
        table.add_column({'key': 'email', 'title': _("Email")}, [{
            'text': (email := t_inst.coach_set.first().email),
            'link': 'mailto:%s' % email,
        } for t_inst in t_institutions])

        handle_question_columns(
            table,
            [t_inst.coach_set.first() for t_inst in t_institutions],
            questions=self.tournament.question_set.filter(for_content_type=ContentType.objects.get_for_model(Coach)).order_by('seq'),
        )

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

        if 'region' in self.tournament.pref('reg_institution_fields'):
            table.add_column({'key': 'region', 'title': _("Region")}, [getattr(t_inst.institution.region, 'name', '') for t_inst in t_institutions])

        handle_question_columns(table, t_institutions)

        return table

    def get_success_url(self):
        return reverse_tournament('reg-institution-list', self.tournament)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs

    def form_valid(self, form):
        qs_before = list(
            self.tournament.tournamentinstitution_set.values_list('institution_id', 'teams_allocated', 'adjudicators_allocated'),
        )
        old_allocations = {inst_id: (teams, adjs) for inst_id, teams, adjs in qs_before}

        form.save()

        coach_ids = []
        for t_inst in self.tournament.tournamentinstitution_set.select_related('institution').prefetch_related('coach_set').all():
            new_teams = t_inst.teams_allocated
            new_adjs = t_inst.adjudicators_allocated
            old_teams, old_adjs = old_allocations.get(t_inst.institution_id, (0, 0))
            if (new_teams, new_adjs) != (old_teams, old_adjs):
                coach_ids.extend([coach.pk for coach in t_inst.coach_set.all() if coach.email])

        subject = self.tournament.pref('slots_allocated_email_subject')
        body = self.tournament.pref('slots_allocated_email_body')
        if coach_ids and subject and body and self.tournament.pref('reg_institution_slots'):
            async_to_sync(get_channel_layer().send)("notifications", {
                "type": "email",
                "message": BulkNotification.EventType.SLOTS_ALLOCATED,
                "extra": {
                    "tournament_id": self.tournament.pk,
                    "url": self.request.build_absolute_uri(
                        reverse_tournament('reg-inst-landing', self.tournament, kwargs={'url_key': '0'}),
                    )[:-2],
                },
                "send_to": coach_ids,
                "subject": subject,
                "body": body,
            })

        messages.success(self.request, _("Successfully modified institution allocations"))

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update(self.tournament.tournamentinstitution_set.aggregate(
            adjs_requested=Sum('adjudicators_requested'),
            adjs_allocated=Sum('adjudicators_allocated'),
            teams_requested=Sum('teams_requested'),
            teams_allocated=Sum('teams_allocated'),
        ))
        kwargs['adjs_registered'] = Adjudicator.objects.all_with_unconfirmed.filter(tournament=self.tournament, institution__isnull=False, adj_core=False, independent=False).count()
        kwargs['teams_registered'] = Team.objects.all_with_unconfirmed.filter(tournament=self.tournament, institution__isnull=False).count()
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

        teams = Team.objects.all_with_unconfirmed.filter(tournament=self.tournament).select_related('institution').prefetch_related(
            'answers__question',
            Prefetch('speaker_set', queryset=Speaker.objects.prefetch_related('answers__question')),
        )
        spk_questions = self.tournament.question_set.filter(for_content_type=ContentType.objects.get_for_model(Speaker)).order_by('seq')

        table = TabbycatTableBuilder(view=self, title=_('Responses'), sort_key='team')
        table.add_team_columns(teams)
        add_confirm_button_column(table, teams, 'reg-team-confirm', self.request)

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
        adjudicators = Adjudicator.objects.all_with_unconfirmed.filter(tournament=self.tournament).select_related('institution').prefetch_related('answers__question')

        table = TabbycatTableBuilder(view=self, title=_('Responses'), sort_key='name')
        table.add_adjudicator_columns(adjudicators, show_metadata=False)
        table.add_column({'key': 'email', 'title': _("Email")}, [adj.email for adj in adjudicators])
        add_confirm_button_column(table, adjudicators, 'reg-adjudicator-confirm', self.request)

        handle_question_columns(table, adjudicators)

        return table


class CustomQuestionFormsetView(TournamentMixin, AdministratorMixin, ModelFormSetView):
    formset_model = Question
    formset_factory_kwargs = {
        'fields': ['tournament', 'for_content_type', 'name', 'text', 'help_text', 'answer_type', 'required', 'min_value', 'max_value', 'choices'],
        'widgets': {
            'tournament': HiddenInput,
            'for_content_type': HiddenInput,
            'help_text': Textarea(attrs={'rows': 3}),
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
            for cat, fields in formset.changed_objects:
                cat.save()

            for i, question in enumerate(formset.new_objects, start=self.get_formset_queryset().aggregate(m=Coalesce(Max('seq'), 0) + 1)['m']):
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


class BaseConfirmRegistrationView(LogActionMixin, TournamentMixin, AdministratorMixin, PostOnlyRedirectView):
    edit_permission = Permission.CONFIRM_REGISTRATION
    action_log_type = ActionLogEntry.ActionType.REGISTRATION_CONFIRM

    def get_object(self):
        return get_object_or_404(self.model.objects.all_with_unconfirmed, tournament=self.tournament, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.registration_status = RegistrationStatus.CONFIRMED
        self.object.save()
        messages.success(request, _("%s has been confirmed.") % getattr(self.object, self.name_field))
        self.log_action()
        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_tournament(self.tournament_redirect_pattern_name, self.tournament)


class ConfirmTeamRegistrationView(BaseConfirmRegistrationView):
    model = Team
    name_field = 'short_name'
    tournament_redirect_pattern_name = 'reg-team-list'


class ConfirmAdjudicatorRegistrationView(BaseConfirmRegistrationView):
    model = Adjudicator
    name_field = 'name'
    tournament_redirect_pattern_name = 'reg-adjudicator-list'


class SlotTransferApprovalView(TournamentMixin, AdministratorMixin, VueTableTemplateView):
    page_emoji = '↔'
    page_title = gettext_lazy("Slot transfer requests")

    view_permission = Permission.VIEW_REGISTRATION

    def get_table(self):
        transfers = SlotTransferRequest.objects.filter(
            tournament=self.tournament,
        ).select_related(
            'source_tournament_institution__institution',
            'receiving_institution__institution',
        ).order_by('-created_at')

        def receiving_inst_cell(transfer):
            if transfer.receiving_institution_id is None:
                return {'text': transfer.receiving_institution_name, 'link': 'mailto:' + transfer.receiving_institution_email if transfer.receiving_institution_email else None}
            return {'text': transfer.receiving_institution.institution.name}

        table = TabbycatTableBuilder(view=self, title=_('Slot transfer requests'))
        table.add_column({'key': 'source_institution', 'title': _("From")}, [t.source_tournament_institution.institution.name for t in transfers])
        table.add_column({'key': 'receiving_institution', 'title': _("To")}, [receiving_inst_cell(t) for t in transfers])
        table.add_column({'key': 'teams_transferred', 'title': _("Teams")}, [t.teams_transferred for t in transfers])
        table.add_column({'key': 'adjudicators_transferred', 'title': _("Adjudicators")}, [t.adjudicators_transferred for t in transfers])
        add_slot_transfer_status_column(table, list(transfers), self.request)
        return table


class UpdateSlotTransferView(TournamentMixin, AdministratorMixin, PostOnlyRedirectView):
    view_permission = Permission.VIEW_REGISTRATION

    def get_object(self):
        return get_object_or_404(SlotTransferRequest, tournament=self.tournament, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        transfer = self.get_object()
        action = request.POST.get('action')
        if action == 'reject':
            transfer.status = SlotTransferRequest.Status.REJECTED
            transfer.save()
            messages.success(request, _("Transfer request rejected."))
            return HttpResponseRedirect(self.get_success_url())

        if action != 'approve' or transfer.status != SlotTransferRequest.Status.PENDING:
            messages.error(request, _("Invalid request or transfer is no longer pending."))
            return HttpResponseRedirect(self.get_success_url())

        # Approve
        TournamentInstitution.objects.filter(id=transfer.source_tournament_institution_id).update(
            teams_allocated=F('teams_allocated') - transfer.teams_transferred,
            adjudicators_allocated=F('adjudicators_allocated') - transfer.adjudicators_transferred,
        )

        invitation = None
        if transfer.receiving_institution_id:
            TournamentInstitution.objects.filter(id=transfer.receiving_institution_id).update(
                teams_allocated=F('teams_allocated') + transfer.teams_transferred,
                adjudicators_allocated=F('adjudicators_allocated') + transfer.adjudicators_transferred,
            )
        else:
            invitation = Invitation(
                tournament=self.tournament,
                for_content_type=ContentType.objects.get_for_model(Institution),
                slot_transfer_request=transfer,
            )
            populate_invitation_url_keys([invitation], self.tournament)
            invitation.save()

        transfer.status = SlotTransferRequest.Status.APPROVED
        transfer.save()

        if invitation:
            reg_url = self.request.build_absolute_uri(
                reverse_tournament('reg-create-institution', self.tournament) + '?key=' + invitation.url_key,
            )
            messages.success(
                request,
                _('Transfer approved. An invitation email has been sent to the provided address. ') + (
                    mark_safe(_('You can also share this link: <a href="%(url)s" class="alert-link">%(url)s</a>') % {'url': reg_url})
                ),
            )
        else:
            messages.success(request, _("Transfer approved."))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_tournament('reg-slot-transfer-approval', self.tournament)


class SlotTransferSummaryView(TournamentMixin, AdministratorMixin, VueTableTemplateView):
    page_emoji = '↔'
    page_title = gettext_lazy("Slot transfer summary")
    view_permission = Permission.VIEW_REGISTRATION

    def get_table(self):
        t_institutions = list(
            self.tournament.tournamentinstitution_set.select_related('institution').order_by('institution__name'),
        )
        approved = SlotTransferRequest.objects.filter(
            tournament=self.tournament,
            status=SlotTransferRequest.Status.APPROVED,
        ).values('receiving_institution_id', 'source_tournament_institution_id', 'teams_transferred', 'adjudicators_transferred')
        net_new_teams = {}
        net_new_adjs = {}
        for t in approved:
            rid = t['receiving_institution_id']
            sid = t['source_tournament_institution_id']
            net_new_teams[rid] = net_new_teams.get(rid, 0) + t['teams_transferred']
            net_new_adjs[rid] = net_new_adjs.get(rid, 0) + t['adjudicators_transferred']
            net_new_teams[sid] = net_new_teams.get(sid, 0) - t['teams_transferred']
            net_new_adjs[sid] = net_new_adjs.get(sid, 0) - t['adjudicators_transferred']

        table = TabbycatTableBuilder(view=self, title=_('Slot transfer summary'))
        table.add_column({'key': 'institution', 'title': _("Institution name")}, [ti.institution.name for ti in t_institutions])
        table.add_column({'key': 'teams_allocated', 'title': _("Teams allocated")}, [ti.teams_allocated for ti in t_institutions])
        table.add_column({'key': 'adjudicators_allocated', 'title': _("Adjudicators allocated")}, [ti.adjudicators_allocated for ti in t_institutions])
        table.add_column({'key': 'teams_net', 'title': _("Net new teams")}, [net_new_teams.get(ti.id, 0) for ti in t_institutions])
        table.add_column({'key': 'adjs_net', 'title': _("Net new adjudicators")}, [net_new_adjs.get(ti.id, 0) for ti in t_institutions])
        return table
