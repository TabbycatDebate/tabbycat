import json
import logging
from itertools import groupby
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max, Prefetch, Q
from django.db.models.functions import Coalesce
from django.forms import HiddenInput
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.html import escape
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.base import View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from adjfeedback.progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam
from draw.models import DebateTeam
from motions.models import RoundMotion
from notifications.models import BulkNotification
from notifications.views import TournamentTemplateEmailCreateView
from options.utils import use_team_code_names
from tournaments.mixins import (PublicTournamentPageMixin,
                                SingleObjectFromTournamentMixin, TournamentMixin)
from tournaments.models import Round
from users.permissions import Permission
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.tables import TabbycatTableBuilder
from utils.views import ModelFormSetView, VueTableTemplateView

from .models import Adjudicator, Institution, Person, Speaker, SpeakerCategory, Team
from .serializers import SpeakerSerializer
from .tables import AdjudicatorDebateTable, TeamDebateTable

logger = logging.getLogger(__name__)


# ==============================================================================
# Lists of things
# ==============================================================================

class BaseParticipantsListView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Participants")
    page_emoji = '🚌'

    def get_tables(self):
        adjudicators = self.tournament.adjudicator_set.select_related('institution')
        adjs_table = TabbycatTableBuilder(view=self, title=_("Adjudicators"), sort_key="name")
        adjs_table.add_adjudicator_columns(adjudicators)

        speakers = Speaker.objects.filter(team__tournament=self.tournament).select_related(
                'team', 'team__institution').prefetch_related('team__speaker_set', 'categories')
        if use_team_code_names(self.tournament, self.admin, user=self.request.user):
            speakers = speakers.order_by('team__code_name')
        else:
            speakers = speakers.order_by('team__short_name')
        speakers_table = TabbycatTableBuilder(view=self, title=_("Speakers"),
                sort_key="team", admin=self.admin)
        speakers_table.add_speaker_columns(speakers)
        speakers_table.add_team_columns([speaker.team for speaker in speakers])

        return [adjs_table, speakers_table]

    def get_context_data(self, **kwargs):
        # These are used to choose the nav display
        kwargs['email_sent'] = BulkNotification.objects.filter(
            tournament=self.tournament, event=BulkNotification.EventType.TEAM_REG).exists()
        return super().get_context_data(**kwargs)


class AdminParticipantsListView(AdministratorMixin, BaseParticipantsListView):
    view_permission = Permission.VIEW_PARTICIPANTS
    template_name = 'participants_list.html'
    admin = True


class AssistantParticipantsListView(AssistantMixin, BaseParticipantsListView):
    admin = True


class PublicParticipantsListView(PublicTournamentPageMixin, BaseParticipantsListView):
    public_page_preference = 'public_participants'
    admin = False
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


class BaseInstitutionsListView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Institutions")
    page_emoji = '🏫'

    def get_table(self):
        institutions = Institution.objects.select_related('region').filter(
            Q(team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament),
        ).annotate(
            nteams=Count('team', distinct=True, filter=Q(
                team__tournament=self.tournament)),
            nadjs=Count('adjudicator', filter=Q(
                adjudicator__tournament=self.tournament, adjudicator__independent=False), distinct=True),
            nias=Count('adjudicator', filter=Q(
                adjudicator__tournament=self.tournament, adjudicator__independent=True), distinct=True),
        ).distinct()

        table = TabbycatTableBuilder(view=self, sort_key='code')
        table.add_column({'key': 'code', 'title': _("Code")}, [escape(i.code) for i in institutions])
        table.add_column({'key': 'name', 'title': _("Full name")}, [escape(i.name) for i in institutions])
        if any(i.region is not None for i in institutions):
            table.add_column({'key': 'region', 'title': _("Region")},
                [escape(i.region.name) if i.region else "—" for i in institutions])
        table.add_column({'key': 'nteams', 'title': _("Teams"), 'tooltip': _("Number of teams")},
            [i.nteams for i in institutions])
        table.add_column({'key': 'nadjs', 'title': _("Adjs"),
            'tooltip': _("Number of adjudicators, excluding independents")},
            [i.nadjs for i in institutions])
        table.add_column({'key': 'nadjs', 'title': _("IAs"),
            'tooltip': _("Number of independent adjudicators")},
            [i.nias for i in institutions])
        return table


class AdminInstitutionsListView(AdministratorMixin, BaseInstitutionsListView):
    view_permission = Permission.VIEW_INSTITUTIONS
    template_name = 'participants_list.html'
    admin = True


class AssistantInstitutionsListView(AssistantMixin, BaseInstitutionsListView):
    admin = True


class PublicInstitutionsListView(PublicTournamentPageMixin, BaseInstitutionsListView):
    public_page_preference = 'public_institutions_list'
    admin = False
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


class InstitutionGenderDiversityView(AdministratorMixin, TournamentMixin, VueTableTemplateView):
    """View showing gender breakdown of speakers and adjudicators by institution."""

    page_title = gettext_lazy("Institution Gender Diversity")
    page_emoji = '📊'
    template_name = 'participants_list.html'
    view_permission = Permission.VIEW_PARTICIPANT_GENDER

    def get_context_data(self, **kwargs):
        kwargs['gender_diversity_nav'] = True
        return super().get_context_data(**kwargs)

    def get_table(self):
        tournament = self.tournament
        gender_choices = dict(Person.GENDER_CHOICES) | {'': _("N/A")}

        # Get institutions with participants in this tournament
        institutions = Institution.objects.filter(
            Q(team__tournament=tournament) | Q(adjudicator__tournament=tournament, adjudicator__independent=False),
        ).distinct().order_by('code')

        speakers = {k: list(v) for k, v in groupby(Speaker.objects.filter(
            team__tournament=tournament,
        ).values('team__institution', 'gender').annotate(
            count=Count('id'),
        ).order_by('team__institution'), key=lambda x: x['team__institution'])}
        adjudicators = {k: list(v) for k, v in groupby(Adjudicator.objects.filter(tournament=tournament, independent=False).values('institution', 'gender').annotate(
            count=Count('id'),
        ).order_by('institution'), key=lambda x: x['institution'])}

        table = TabbycatTableBuilder(view=self, sort_key='institution')

        table.add_column(
            {'key': 'institution', 'title': _("Institution")},
            [inst.name for inst in institutions],
        )
        for gender, label in gender_choices.items():
            table.add_column(
                {'key': f'speaker_{gender}', 'title': _("Speakers (%(gender)s)") % {'gender': label}},
                [next((s['count'] for s in speakers.get(inst.id, []) if s['gender'] == gender), 0) for inst in institutions],
            )
        for gender, label in gender_choices.items():
            table.add_column(
                {'key': f'adjudicator_{gender}', 'title': _("Adjudicators (%(gender)s)") % {'gender': label}},
                [next((s['count'] for s in adjudicators.get(inst.id, []) if s['gender'] == gender), 0) for inst in institutions],
            )

        return table


class BaseCodeNamesListView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Code Names")
    page_emoji = '🕵'

    def get_table(self):
        t = self.tournament
        teams = t.team_set.select_related('institution').prefetch_related('speaker_set')
        table = TabbycatTableBuilder(view=self, sort_key='code_name')
        table.add_column(
            {'key': 'code_name', 'title': _("Code name")},
            [{'text': escape(t.code_name) or "—"} for t in teams],
        )
        table.add_team_columns(teams)
        return table


class AdminCodeNamesListView(AdministratorMixin, BaseCodeNamesListView):
    template_name = 'participants_list.html'
    view_permission = Permission.VIEW_DECODED_TEAMS


class AssistantCodeNamesListView(AssistantMixin, BaseCodeNamesListView):
    pass


# ==============================================================================
# Email page
# ==============================================================================

class EmailTeamRegistrationView(TournamentTemplateEmailCreateView):
    page_subtitle = _("Team Registration")

    event = BulkNotification.EventType.TEAM_REG
    subject_template = 'team_email_subject'
    message_template = 'team_email_message'

    tournament_redirect_pattern_name = 'participants-list'

    def get_queryset(self):
        return Speaker.objects.filter(team__tournament=self.tournament).select_related('team').prefetch_related('team__speaker_set')

    def get_table(self):
        table = super().get_table()

        table.add_team_columns([s.team for s in self.get_queryset()])
        return table


# ==============================================================================
# Team and adjudicator record pages
# ==============================================================================

class BaseRecordView(SingleObjectFromTournamentMixin, VueTableTemplateView):

    allow_null_tournament = True

    def get_queryset(self):
        qs = super().get_queryset() if not self.admin else self.model.objects.all_with_unconfirmed.filter(
            Q(tournament=self.tournament) | Q(tournament__isnull=self.allow_null_tournament),
        )
        return qs.select_related('tournament', 'institution__region')

    def use_team_code_names(self):
        return use_team_code_names(self.tournament, self.admin, user=self.request.user)

    @staticmethod
    def allocations_set(obj, admin, tournament):
        model_related = {'Team': 'debateteam_set', 'Adjudicator': 'debateadjudicator_set'}[type(obj).__name__]
        draw_statuses = [Round.Status.RELEASED, Round.Status.TEAMS_RELEASED] if type(obj).__name__ == 'Team' else [Round.Status.RELEASED]
        try:
            qs = getattr(obj, model_related).filter(
                debate__round__in=tournament.current_rounds).select_related('debate__round')
            if admin:
                qs = qs.prefetch_related(Prefetch('debate__round__roundmotion_set',
                    queryset=RoundMotion.objects.select_related('motion')))
            else:
                qs = qs.filter(debate__round__draw_status__in=draw_statuses).prefetch_related(
                    Prefetch('debate__round__roundmotion_set',
                        queryset=RoundMotion.objects.filter(round__motions_status=Round.MotionsStatus.MOTIONS_RELEASED).select_related('motion')))
            return qs
        except ObjectDoesNotExist:
            return None

    @property
    def draw_released(self):
        return self.tournament.current_round.draw_status == Round.Status.RELEASED

    def get_context_data(self, **kwargs):
        kwargs['admin_page'] = self.admin
        kwargs['draw_released'] = self.draw_released
        kwargs['use_code_names'] = self.use_team_code_names()
        kwargs[self.model_kwarg] = self.allocations_set(self.object, self.admin, self.tournament)

        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class BaseTeamRecordView(BaseRecordView):

    model = Team
    model_kwarg = 'debateteams'
    template_name = 'team_record.html'

    table_title = _("Results")

    def get_queryset(self):
        return super().get_queryset().prefetch_related('break_categories')

    def get_page_title(self):
        # This has to be in Python so that the emoji can be team-dependent.
        name = self.object.code_name if self.use_team_code_names() else self.object.long_name
        return _("Record for %(name)s") % {'name': name}

    def get_page_emoji(self):
        if self.tournament.pref('show_emoji'):
            return self.object.emoji

    @property
    def draw_released(self):
        return self.tournament.current_round.draw_status in [Round.Status.RELEASED, Round.Status.TEAMS_RELEASED]

    def get_context_data(self, **kwargs):
        kwargs['team_short_name'] = self.object.code_name if self.use_team_code_names() else self.object.short_name
        kwargs['feedback_progress'] = FeedbackProgressForTeam(self.object, self.tournament)
        return super().get_context_data(**kwargs)

    def get_table(self):
        return TeamDebateTable.get_table(self, self.object)


class BaseAdjudicatorRecordView(BaseRecordView):

    model = Adjudicator
    model_kwarg = 'debateadjudications'
    template_name = 'adjudicator_record.html'
    page_emoji = '⚖'

    table_title = _("Previous Rounds")

    def _get_adj_adj_conflicts(self):
        adjs = []
        for ac in self.object.adjudicatoradjudicatorconflict_source_set.all():
            adjs.append(ac.adjudicator2)
        for ac in self.object.adjudicatoradjudicatorconflict_target_set.all():
            adjs.append(ac.adjudicator1)
        return adjs

    def get_context_data(self, **kwargs):
        kwargs['feedback_progress'] = FeedbackProgressForAdjudicator(self.object, self.tournament)
        kwargs['adjadj_conflicts'] = self._get_adj_adj_conflicts()
        return super().get_context_data(**kwargs)

    def get_table(self):
        return AdjudicatorDebateTable.get_table(self, self.object)


class TeamRecordView(AdministratorMixin, BaseTeamRecordView):
    admin = True
    view_permission = Permission.VIEW_TEAMS

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'teaminstitutionconflict_set__institution',
            'adjudicatorteamconflict_set__adjudicator',
            'venue_constraints__category',
            'answers__question',
            'break_categories',
            Prefetch('speaker_set', queryset=Speaker.objects.all().prefetch_related('answers__question', 'categories')),
        )


class AdjudicatorRecordView(AdministratorMixin, BaseAdjudicatorRecordView):
    admin = True
    view_permission = Permission.VIEW_ADJUDICATORS

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'adjudicatorinstitutionconflict_set__institution',
            'adjudicatorteamconflict_set__team',
            'venue_constraints__category',
            'answers__question',
        )


class PublicTeamRecordView(PublicTournamentPageMixin, BaseTeamRecordView):
    public_page_preference = 'public_record'
    admin = False


class PublicAdjudicatorRecordView(PublicTournamentPageMixin, BaseAdjudicatorRecordView):
    public_page_preference = 'public_record'
    admin = False


# ==============================================================================
# Speaker categories
# ==============================================================================

class EditSpeakerCategoriesView(LogActionMixin, AdministratorMixin, TournamentMixin, ModelFormSetView):
    # The tournament is included in the form as a hidden input so that
    # uniqueness checks will work. Since this is a superuser form, they can
    # access all tournaments anyway, so tournament forgery wouldn't be a
    # security risk.
    view_permission = Permission.VIEW_SPEAKER_CATEGORIES
    template_name = 'speaker_categories_edit.html'
    formset_model = SpeakerCategory
    action_log_type = ActionLogEntry.ActionType.SPEAKER_CATEGORIES_EDIT

    url_name = 'participants-speaker-categories-edit'
    success_url = 'participants-list'

    def get_formset_factory_kwargs(self):
        return {
            'fields': ('name', 'tournament', 'slug', 'limit', 'public'),
            'extra': 2,
            'widgets': {
                'tournament': HiddenInput,
            },
        }

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(tournament=self.tournament)

    def get_formset_kwargs(self):
        return {
            'initial': [{'tournament': self.tournament}] * 2,
        }

    def prepare_related(self, cat):
        pass

    def formset_valid(self, formset):
        cats = formset.save(commit=False)

        for cat, fields in formset.changed_objects:
            cat.save()

        for i, cat in enumerate(formset.new_objects, start=self.get_formset_queryset().aggregate(m=Coalesce(Max('seq'), 0) + 1)['m']):
            cat.seq = i
            cat.tournament = self.tournament  # Even with the tournament in the form, avoid it being changed
            cat.save()

            self.prepare_related(cat)

        if cats:
            message = ngettext("Saved category: %(list)s",
                "Saved categories: %(list)s",
                len(cats),
            ) % {'list': ", ".join(category.name for category in cats)}
            messages.success(self.request, message)
        else:
            messages.success(self.request, _("No changes were made to the categories."))
        if "add_more" in self.request.POST:
            return redirect_tournament(self.url_name, self.tournament)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament(self.success_url, self.tournament)


class EditSpeakerCategoryEligibilityView(AdministratorMixin, TournamentMixin, VueTableTemplateView):

    # form_class = forms.SpeakerCategoryEligibilityForm
    template_name = 'edit_speaker_eligibility.html'
    page_title = _("Speaker Category Eligibility")
    page_emoji = '🍯'
    edit_permission = Permission.EDIT_SPEAKER_ELIGIBILITY

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key='team')
        speakers = Speaker.objects.filter(team__tournament=self.tournament).select_related(
            'team', 'team__institution').prefetch_related('categories', 'team__speaker_set')
        table.add_speaker_columns(speakers, categories=False)
        table.add_team_columns([speaker.team for speaker in speakers])
        speaker_categories = self.tournament.speakercategory_set.all()

        for sc in speaker_categories:
            table.add_column({'key': escape(sc.name), 'title': escape(sc.name)}, [{
                'component': 'check-cell',
                'checked': True if sc in speaker.categories.all() else False,
                'id': speaker.id,
                'type': sc.id,
            } for speaker in speakers])
        return table

    def get_context_data(self, **kwargs):
        speaker_categories = self.tournament.speakercategory_set.all()
        json_categories = SpeakerSerializer(speaker_categories, many=True).data
        kwargs["speaker_categories"] = json.dumps(json_categories)
        kwargs["speaker_categories_length"] = speaker_categories.count()
        kwargs["save"] = reverse_tournament('participants-speaker-update-eligibility', self.tournament)
        return super().get_context_data(**kwargs)


class UpdateEligibilityEditView(LogActionMixin, AdministratorMixin, TournamentMixin, View):
    action_log_type = ActionLogEntry.ActionType.SPEAKER_ELIGIBILITY_EDIT
    participant_model = Speaker
    many_to_many_field = 'categories'
    edit_permission = Permission.EDIT_SPEAKER_ELIGIBILITY

    def set_category_eligibility(self, participant, sent_status):
        category_id = sent_status['type']
        many_to_many_model = getattr(participant, self.many_to_many_field)
        marked_eligible = category_id in {c.id for c in many_to_many_model.all()}
        if sent_status['checked'] and not marked_eligible:
            many_to_many_model.add(category_id)
        elif not sent_status['checked'] and marked_eligible:
            many_to_many_model.remove(category_id)

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)

        try:
            participant_ids = [int(key) for key in posted_info.keys()]
            participants = self.participant_model.objects.prefetch_related(self.many_to_many_field).in_bulk(participant_ids)
            for participant_id, participant in participants.items():
                self.set_category_eligibility(participant, posted_info[str(participant_id)])
            self.log_action()
        except Exception:
            message = "Error handling eligibility updates"
            logger.exception(message)
            return JsonResponse({'status': 'false', 'message': message}, status=500)

        return JsonResponse(json.dumps(True), safe=False)


class InstitutionAdjRuleView(TournamentMixin, AdministratorMixin, VueTableTemplateView):

    page_title = gettext_lazy("Adjudicator Requirement")
    page_emoji = '🔨'
    template_name = 'participants_list.html'
    admin = True

    RULES = {
        'N-1': lambda a, t: a < t - 1,
    }

    def get_table(self):

        rounds = self.tournament.round_set.filter(stage=Round.Stage.PRELIMINARY).exclude(draw_status=Round.Status.NONE)
        institutions = Institution.objects.filter(
            Q(adjudicator__tournament=self.tournament) | Q(team__tournament=self.tournament),
        ).distinct()
        inst_teams = DebateTeam.objects.filter(
            debate__round__stage=Round.Stage.PRELIMINARY,
            team__tournament=self.tournament, team__institution_id__isnull=False,
        ).exclude(
            debate__round__draw_status=Round.Status.NONE,
        ).order_by('team__institution_id').values('debate__round_id', 'team__institution_id').annotate(Count('id'))
        inst_adju = DebateAdjudicator.objects.filter(
            debate__round__stage=Round.Stage.PRELIMINARY,
            adjudicator__tournament=self.tournament, adjudicator__institution_id__isnull=False,
        ).exclude(
            debate__round__draw_status=Round.Status.NONE,
        ).order_by('adjudicator__institution_id').values('debate__round_id', 'adjudicator__institution_id').annotate(Count('id'))

        reg_teams = {r['institution_id']: r['id__count'] for r in Team.objects.values('institution_id').annotate(Count('id'))}
        reg_adjs = {
            r['institution_id']: r['id__count'] for r in Adjudicator.objects.filter(independent=False).values('institution_id').annotate(Count('id'))
        }

        for inst_id, group in groupby(inst_teams, key=itemgetter('team__institution_id')):
            institution = next((i for i in institutions if i.id == inst_id), None)
            for r in group:
                setattr(institution, 'r_%d_teams' % r['debate__round_id'], r['id__count'])
        for inst_id, group in groupby(inst_adju, key=itemgetter('adjudicator__institution_id')):
            institution = next((i for i in institutions if i.id == inst_id), None)
            for r in group:
                setattr(institution, 'r_%d_adjudicators' % r['debate__round_id'], r['id__count'])

        table = TabbycatTableBuilder(
            view=self,
            data=institutions,
            sort_key='code_name',
        )

        table.add_column(
            {'key': 'code_name', 'title': _("Institution")},
            [inst.code for inst in institutions],
        )

        def create_inst_cell(round_id, inst, teams=0, adju=0):
            teams = getattr(inst, f"r_{round_id}_teams", teams)
            adju = getattr(inst, f"r_{round_id}_adjudicators", adju)

            cell = {'text': f"{teams}/{adju}"}

            if self.RULES['N-1'](adju, teams):
                cell['class'] = 'text-danger'
            return cell

        table.add_column(
            {'key': 'reg', 'title': _("Registered")},
            [create_inst_cell(0, inst, reg_teams[inst.id], reg_adjs[inst.id]) for inst in institutions],
        )

        for round in rounds:
            table.add_column(
                {
                    'key': f'round_{round.id}',
                    'title': round.name,
                },
                [create_inst_cell(round.id, inst) for inst in institutions],
            )

        return table

    def get_context_data(self, **kwargs):
        # These are used to choose the nav display
        kwargs['adj_req_nav'] = True
        return super().get_context_data(**kwargs)
