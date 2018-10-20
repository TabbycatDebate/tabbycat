import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Prefetch, Q
from django.forms import HiddenInput
from django.http import JsonResponse
from django.utils.translation import gettext_lazy, ngettext
from django.utils.translation import gettext as _
from django.views.generic.base import View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from adjfeedback.progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam
from draw.prefetch import populate_opponents
from notifications.models import SentMessageRecord
from options.utils import use_team_code_names
from results.models import SpeakerScore, TeamScore
from results.prefetch import populate_confirmed_ballots, populate_wins
from tournaments.mixins import (PublicTournamentPageMixin, SingleObjectByRandomisedUrlMixin,
                                SingleObjectFromTournamentMixin, TournamentMixin)
from tournaments.models import Round
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.views import ModelFormSetView, VueTableTemplateView
from utils.tables import TabbycatTableBuilder

from .models import Adjudicator, Institution, Speaker, SpeakerCategory, Team
from .tables import TeamResultTableBuilder

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
        if use_team_code_names(self.tournament, self.admin):
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
        kwargs['email_sent'] = SentMessageRecord.objects.filter(
            tournament=self.tournament, event=SentMessageRecord.EVENT_TYPE_TEAM).exists()
        return super().get_context_data(**kwargs)


class AdminParticipantsListView(AdministratorMixin, BaseParticipantsListView):
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
            Q(team__tournament=self.tournament) | Q(adjudicator__tournament=self.tournament)
        ).annotate(
            nteams=Count('team', distinct=True),
            nadjs=Count('adjudicator', filter=Q(adjudicator__independent=False), distinct=True),
            nias=Count('adjudicator', filter=Q(adjudicator__independent=True), distinct=True),
        ).distinct()

        table = TabbycatTableBuilder(view=self, sort_key='code')
        table.add_column({'key': 'code', 'title': _("Code")}, [i.code for i in institutions])
        table.add_column({'key': 'name', 'title': _("Full name")}, [i.name for i in institutions])
        if any(i.region is not None for i in institutions):
            table.add_column({'key': 'region', 'title': _("Region")},
                [i.region.name if i.region else "—" for i in institutions])
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
    template_name = 'participants_list.html'
    admin = True


class AssistantInstitutionsListView(AssistantMixin, BaseInstitutionsListView):
    admin = True


class PublicInstitutionsListView(PublicTournamentPageMixin, BaseInstitutionsListView):
    public_page_preference = 'public_institutions_list'
    admin = False
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT


class BaseCodeNamesListView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Code Names")
    page_emoji = '🕵'

    def get_table(self):
        t = self.tournament
        teams = t.team_set.select_related('institution').prefetch_related('speaker_set')
        table = TabbycatTableBuilder(view=self, sort_key='code_name')
        table.add_column(
            {'key': 'code_name', 'title': _("Code name")},
            [{'text': t.code_name or "—"} for t in teams]
        )
        table.add_team_columns(teams)
        return table


class AdminCodeNamesListView(AdministratorMixin, BaseCodeNamesListView):
    template_name = 'participants_list.html'


class AssistantCodeNamesListView(AssistantMixin, BaseCodeNamesListView):
    pass


# ==============================================================================
# Team and adjudicator record pages
# ==============================================================================

class BaseRecordView(SingleObjectFromTournamentMixin, VueTableTemplateView):

    allow_null_tournament = True

    def use_team_code_names(self):
        return use_team_code_names(self.tournament, self.admin)

    def get_context_data(self, **kwargs):
        kwargs['admin_page'] = self.admin
        kwargs['draw_released'] = self.tournament.current_round.draw_status == Round.STATUS_RELEASED
        kwargs['use_code_names'] = self.use_team_code_names()
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class BaseTeamRecordView(BaseRecordView):

    model = Team
    template_name = 'team_record.html'

    def get_page_title(self):
        # This has to be in Python so that the emoji can be team-dependent.
        name = self.object.code_name if self.use_team_code_names() else self.object.long_name
        return _("Record for %(name)s") % {'name': name}

    def get_page_emoji(self):
        if self.tournament.pref('show_emoji'):
            return self.object.emoji

    def get_context_data(self, **kwargs):
        tournament = self.tournament

        try:
            kwargs['debateteams'] = self.object.debateteam_set.select_related(
                'debate__round').prefetch_related('debate__round__motion_set').filter(
                debate__round=tournament.current_round)
        except ObjectDoesNotExist:
            kwargs['debateteams'] = None

        kwargs['team_short_name'] = self.object.code_name if self.use_team_code_names() else self.object.short_name
        kwargs['feedback_progress'] = FeedbackProgressForTeam(self.object, tournament)

        return super().get_context_data(**kwargs)

    def get_table(self):
        """On team record pages, the table is the results table."""
        tournament = self.tournament
        teamscores = TeamScore.objects.filter(
            debate_team__team=self.object,
            ballot_submission__confirmed=True,
        ).select_related(
            'debate_team__debate__round__tournament'
        ).prefetch_related(
            Prefetch('debate_team__debate__debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator__institution')),
            'debate_team__debate__debateteam_set__team',
            'debate_team__debate__round__motion_set',
            Prefetch('debate_team__speakerscore_set',
                queryset=SpeakerScore.objects.filter(ballot_submission__confirmed=True).select_related('speaker').order_by('position'),
                to_attr='speaker_scores'),
        ).order_by('debate_team__debate__round__seq')

        if not self.admin and not tournament.pref('all_results_released'):
            teamscores = teamscores.filter(
                debate_team__debate__round__draw_status=Round.STATUS_RELEASED,
                debate_team__debate__round__silent=False,
                debate_team__debate__round__completed=True,
            )

        debates = [ts.debate_team.debate for ts in teamscores]
        populate_opponents([ts.debate_team for ts in teamscores])
        populate_confirmed_ballots(debates, motions=True, results=True)

        table = TeamResultTableBuilder(view=self, title=_("Results"), sort_key="round")
        table.add_round_column([debate.round for debate in debates])
        table.add_debate_result_by_team_column(teamscores)
        table.add_cumulative_team_points_column(teamscores)
        if self.admin or tournament.pref('all_results_released') and tournament.pref('speaker_tab_released') and tournament.pref('speaker_tab_limit') == 0:
                table.add_speaker_scores_column(teamscores)
        table.add_debate_side_by_team_column(teamscores)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if self.admin or tournament.pref('public_motions'):
            table.add_debate_motion_column(debates)

        table.add_debate_ballot_link_column(debates)

        return table


class BaseAdjudicatorRecordView(BaseRecordView):

    model = Adjudicator
    template_name = 'adjudicator_record.html'
    page_emoji = '⚖'

    def get_page_title(self):
        return _("Record for %(name)s") % {'name': self.object.name}

    def get_context_data(self, **kwargs):
        try:
            kwargs['debateadjudications'] = self.object.debateadjudicator_set.filter(
                debate__round=self.tournament.current_round
            ).select_related(
                'debate__round'
            ).prefetch_related(
                'debate__round__motion_set'
            )
        except ObjectDoesNotExist:
            kwargs['debateadjudications'] = None

        kwargs['feedback_progress'] = FeedbackProgressForAdjudicator(self.object, self.tournament)

        return super().get_context_data(**kwargs)

    def get_table(self):
        """On adjudicator record pages, the table is the previous debates table."""
        debateadjs = DebateAdjudicator.objects.filter(
            adjudicator=self.object,
        ).select_related(
            'debate__round'
        ).prefetch_related(
            Prefetch('debate__debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator__institution')),
            'debate__debateteam_set__team__speaker_set',
            'debate__round__motion_set',
        )
        if not self.admin and not self.tournament.pref('all_results_released'):
            debateadjs = debateadjs.filter(
                debate__round__draw_status=Round.STATUS_RELEASED,
                debate__round__silent=False,
                debate__round__completed=True,
            )
        debates = [da.debate for da in debateadjs]
        populate_wins(debates)
        populate_confirmed_ballots(debates, motions=True, results=True)

        table = TabbycatTableBuilder(view=self, title=_("Previous Rounds"), sort_key="round")
        table.add_round_column([debate.round for debate in debates])
        table.add_debate_results_columns(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True, highlight_adj=self.object)

        if self.admin or self.tournament.pref('public_motions'):
            table.add_debate_motion_column(debates)

        table.add_debate_ballot_link_column(debates)
        return table


class TeamRecordView(AdministratorMixin, BaseTeamRecordView):
    admin = True


class AdjudicatorRecordView(AdministratorMixin, BaseAdjudicatorRecordView):
    admin = True


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

    template_name = 'speaker_categories_edit.html'
    formset_model = SpeakerCategory
    action_log_type = ActionLogEntry.ACTION_TYPE_SPEAKER_CATEGORIES_EDIT

    def get_formset_factory_kwargs(self):
        return {
            'fields': ('name', 'tournament', 'slug', 'seq', 'limit', 'public'),
            'extra': 2,
            'widgets': {
                'tournament': HiddenInput
            }
        }

    def get_formset_queryset(self):
        return SpeakerCategory.objects.filter(tournament=self.tournament)

    def get_formset_kwargs(self):
        return {
            'initial': [{'tournament': self.tournament}] * 2,
        }

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        if self.instances:
            message = ngettext("Saved speaker category: %(list)s",
                "Saved speaker categories: %(list)s",
                len(self.instances)
            ) % {'list': ", ".join(category.name for category in self.instances)}
            messages.success(self.request, message)
        else:
            messages.success(self.request, _("No changes were made to the speaker categories."))
        if "add_more" in self.request.POST:
            return redirect_tournament('participants-speaker-categories-edit', self.tournament)
        return result

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('participants-list', self.tournament)


class EditSpeakerCategoryEligibilityView(AdministratorMixin, TournamentMixin, VueTableTemplateView):

    # form_class = forms.SpeakerCategoryEligibilityForm
    template_name = 'edit_speaker_eligibility.html'
    page_title = _("Speaker Category Eligibility")
    page_emoji = '🍯'

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key='team')
        speakers = Speaker.objects.filter(team__tournament=self.tournament).select_related(
            'team', 'team__institution').prefetch_related('categories', 'team__speaker_set')
        table.add_speaker_columns(speakers, categories=False)
        table.add_team_columns([speaker.team for speaker in speakers])
        speaker_categories = self.tournament.speakercategory_set.all()

        for sc in speaker_categories:
            table.add_column({'key': sc.name, 'title': sc.name}, [{
                'component': 'check-cell',
                'checked': True if sc in speaker.categories.all() else False,
                'id': speaker.id,
                'type': sc.id
            } for speaker in speakers])
        return table

    def get_context_data(self, **kwargs):
        speaker_categories = self.tournament.speakercategory_set.all()
        json_categories = [bc.serialize for bc in speaker_categories]
        kwargs["speaker_categories"] = json.dumps(json_categories)
        kwargs["speaker_categories_length"] = speaker_categories.count()
        kwargs["save"] = reverse_tournament('participants-speaker-update-eligibility', self.tournament)
        return super().get_context_data(**kwargs)


class UpdateEligibilityEditView(LogActionMixin, AdministratorMixin, TournamentMixin, View):
    action_log_type = ActionLogEntry.ACTION_TYPE_SPEAKER_ELIGIBILITY_EDIT

    def set_category_eligibility(self, speaker, sent_status):
        category_id = sent_status['type']
        marked_eligible = category_id in [c.id for c in speaker.categories.all()]
        if sent_status['checked'] and not marked_eligible:
            speaker.categories.add(category_id)
            speaker.save()
        elif not sent_status['checked'] and marked_eligible:
            speaker.categories.remove(category_id)
            speaker.save()

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)

        try:
            speaker_ids = [int(key) for key in posted_info.keys()]
            speakers = Speaker.objects.prefetch_related('categories').in_bulk(speaker_ids)
            for speaker_id, speaker in speakers.items():
                self.set_category_eligibility(speaker, posted_info[str(speaker_id)])
            self.log_action()
        except:
            message = "Error handling eligiblity updates"
            logger.exception(message)
            return JsonResponse({'status': 'false', 'message': message}, status=500)

        return JsonResponse(json.dumps(True), safe=False)


# ==============================================================================
# Shift scheduling
# ==============================================================================

class PublicConfirmShiftView(SingleObjectByRandomisedUrlMixin, ModelFormSetView):
    # Django doesn't have a class-based view for formsets, so this implements
    # the form processing analogously to FormView, with less decomposition.
    # See also: motions.views.EditMotionsView.

    public_page_preference = 'allocation_confirmations'
    template_name = 'confirm_shifts.html'
    formset_factory_kwargs = dict(can_delete=False, extra=0, fields=['timing_confirmed'])
    model = Adjudicator
    allow_null_tournament = True
    formset_model = DebateAdjudicator

    def get_success_url(self):
        return reverse_tournament('participants-public-confirm-shift',
                self.tournament, kwargs={'url_key': self.object.url_key})

    def get_formset_queryset(self):
        return self.object.debateadjudicator_set.all()

    def get_context_data(self, **kwargs):
        kwargs['adjudicator'] = self.get_object()
        return super().get_context_data(**kwargs)

    def formset_valid(self, formset):
        messages.success(self.request, _("Your shift check-ins have been saved"))
        return super().formset_valid(formset)

    def formset_invalid(self, formset):
        messages.error(self.request, _("Whoops! There was a problem with the form."))
        return super().formset_invalid(formset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
