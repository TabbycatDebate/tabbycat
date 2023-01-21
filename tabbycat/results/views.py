import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import ProgrammingError
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.generic import FormView, TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from draw.prefetch import populate_opponents
from motions.models import RoundMotion
from motions.utils import merge_motion_vetos, merge_motions
from notifications.models import BulkNotification
from options.utils import use_team_code_names, use_team_code_names_data_entry
from participants.models import Adjudicator
from participants.templatetags.team_name_for_data_entry import team_name_for_data_entry
from tournaments.mixins import (CurrentRoundMixin, PersonalizablePublicTournamentPageMixin, PublicTournamentPageMixin,
                                RoundMixin, SingleObjectByRandomisedUrlMixin, SingleObjectFromTournamentMixin,
                                TournamentMixin)
from tournaments.models import Round
from utils.misc import get_ip_address, reverse_round, reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin
from utils.tables import TabbycatTableBuilder
from utils.views import PostOnlyRedirectView, VueTableTemplateView

from .consumers import BallotStatusConsumer
from .forms import (PerAdjudicatorBallotSetForm, PerAdjudicatorEliminationBallotSetForm, SingleBallotSetForm,
                    SingleEliminationBallotSetForm)
from .models import BallotSubmission, TeamScore
from .prefetch import populate_confirmed_ballots, populate_results
from .result import DebateResult, get_class_name, ResultError
from .tables import ResultsTableBuilder
from .utils import get_status_meta, populate_identical_ballotsub_lists

logger = logging.getLogger(__name__)


class PublicResultsIndexView(PublicTournamentPageMixin, TemplateView):

    template_name = 'public_results_index.html'
    public_page_preference = 'public_results'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT

    def get_context_data(self, **kwargs):
        kwargs["rounds"] = self.tournament.round_set.filter(
            completed=True, silent=False).order_by('seq')
        return super().get_context_data(**kwargs)


# ==============================================================================
# Views that show the results for all rounds in a debate
# ==============================================================================

class BaseResultsEntryForRoundView(RoundMixin, VueTableTemplateView):

    def _get_draw(self):
        if not hasattr(self, '_draw'):
            self._draw = self.round.debate_set_with_prefetches(
                    ordering=('room_rank',), results=True, wins=True, check_ins=True, iron=True)
        return self._draw

    def get_table(self):
        draw = self._get_draw()
        table = ResultsTableBuilder(view=self, sort_key="status")
        table.add_ballot_check_in_columns(draw, key="check_ins")
        table.add_ballot_status_columns(draw, key="status")
        table.add_ballot_entry_columns(draw, self.view_role, self.request.user)
        if self.tournament.pref('enable_postponements'):
            table.add_debate_postponement_column(draw)
        table.add_debate_venue_columns(draw, for_admin=True)
        table.add_debate_results_columns(draw, iron=True)
        table.add_debate_adjudicators_column(draw, show_splits=True, for_admin=True)
        return table

    def get_irons_list(self):
        iron_speeches = []
        use_code_names = use_team_code_names_data_entry(self.tournament, True)
        for d in self._get_draw():
            for side in self.tournament.sides:
                debateteam = d.get_dt(side)
                if debateteam.iron > 0 or debateteam.iron_prev:
                    iron_speeches.append({
                        'venue': d.venue.display_name if d.venue else None,
                        'team': team_name_for_data_entry(debateteam.team, use_code_names),
                        'current_round': debateteam.iron,
                        'previous_round': debateteam.iron_prev,
                    })
        return iron_speeches

    def get_context_data(self, **kwargs):
        kwargs["incomplete_ballots"] = self._get_draw().filter(
            Q(result_status=Debate.STATUS_NONE) | Q(result_status=Debate.STATUS_DRAFT)).exists()
        kwargs["iron_speeches"] = self.get_irons_list()
        return super().get_context_data(**kwargs)


class AssistantResultsEntryView(AssistantMixin, CurrentRoundMixin, BaseResultsEntryForRoundView):
    template_name = 'assistant_results.html'


class AdminResultsEntryForRoundView(AdministratorMixin, BaseResultsEntryForRoundView):
    template_name = 'admin_results.html'

    def get_context_data(self, **kwargs):
        # Stopgap to warn user about potential database inconsistency, when
        # trainee adjudicators seem to have given scores. This normally happens
        # when an adjudicator was demoted after a result was entered.
        # See: https://github.com/TabbycatDebate/tabbycat/issues/922
        # This stopgap should be deleted after a more general data consistency
        # solution is implemented.
        kwargs["debates_with_trainee_scoresheets"] = [
            f"{debate.matchup} ({debate.venue.name})"
            for debate in self.round.debate_set_with_prefetches(
                teams=True, venues=True, adjudicators=False, speakers=False,
                wins=False, results=False, institutions=False, check_ins=False, iron=False,
                filter_kwargs={
                    'ballotsubmission__speakerscorebyadj__debate_adjudicator__type':
                        DebateAdjudicator.TYPE_TRAINEE,
                },
                ordering=None,
            ).select_related('round__tournament').distinct()
            # TODO: The select_related() call above avoids an N+1 issue in the
            # call to self.round.tournament.sides in debate.matchup. If this
            # also happens elsewhere, it might be worth digging into.
        ]

        # Another warning about potential database inconsistency, but this one's
        # only ever happened as a consequence of direct database edits via SQL,
        # so we've probably already got all the consistency checks we can
        # reasonably have. This is just an extra courtesy for users who try to
        # hack too much. Just check `exists()`, no further information---it's
        # not worth the performance hit to do this work for them.
        multiple_confirmed_ballots_found = self.round.debate_set.annotate(
            num_ballots=Count('ballotsubmission', filter=Q(ballotsubmission__confirmed=True)),
        ).filter(num_ballots__gt=1).exists()
        if multiple_confirmed_ballots_found:
            logger.error("Multiple confirmed ballots for a single debate found")
        kwargs["debates_with_multiple_confirmed_ballots_found"] = multiple_confirmed_ballots_found

        return super().get_context_data(**kwargs)


class PublicResultsForRoundView(RoundMixin, PublicTournamentPageMixin, VueTableTemplateView):

    template_name = "public_results_for_round.html"
    public_page_preference = 'public_results'
    page_title = gettext_lazy("Results")
    page_emoji = '💥'
    default_view = 'team'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT

    def get_table(self):
        view_type = self.request.session.get('results_view', self.default_view)
        if view_type == 'debate':
            return self.get_table_by_debate()
        else:
            return self.get_table_by_team()

    def get_table_by_debate(self):
        debates = self.round.debate_set_with_prefetches(results=True,
                wins=True, institutions=True, adjudicators=True)
        populate_confirmed_ballots(debates, motions=True,
                results=self.round.ballots_per_debate == 'per-adj')

        table = TabbycatTableBuilder(view=self, sort_key="venue")
        table.add_debate_venue_columns(debates)
        table.add_debate_results_columns(debates)
        if not (self.tournament.pref('teams_in_debate') == 'bp' and self.round.is_break_round):
            table.add_debate_ballot_link_column(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if self.tournament.pref('show_motions_in_results'):
            table.add_debate_motion_column(debates)

        return table

    def get_table_by_team(self):
        teamscores = TeamScore.objects.filter(
            debate_team__debate__round=self.round,
            ballot_submission__confirmed=True).prefetch_related(
            'debate_team__team__speaker_set',
            'debate_team__debate__debateadjudicator_set__adjudicator',
            'debate_team__debate__debateadjudicator_set__adjudicator__institution',
            'debate_team__debate__debateteam_set__team').select_related(
            'ballot_submission',
            'debate_team__team__institution',
            'debate_team__debate__round')
        debates = [ts.debate_team.debate for ts in teamscores]

        if self.tournament.pref('teams_in_debate') == 'two':
            populate_opponents([ts.debate_team for ts in teamscores])
        populate_confirmed_ballots(debates, motions=True,
            results=self.round.ballots_per_debate == 'per-adj')

        table = TabbycatTableBuilder(view=self, sort_key="team")
        table.add_team_columns([ts.debate_team.team for ts in teamscores])
        table.add_debate_result_by_team_column(teamscores)
        table.add_debate_side_by_team_column(teamscores, self.tournament)
        if not (self.tournament.pref('teams_in_debate') == 'bp' and self.round.is_break_round):
            table.add_debate_ballot_link_column(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if self.tournament.pref('show_motions_in_results'):
            table.add_debate_motion_column(debates)

        return table

    def get(self, request, *args, **kwargs):
        if self.round.silent and not self.tournament.pref('all_results_released'):
            logger.warning("Refused results for %s: silent", self.round.name)
            return render(request, 'public_results_silent.html', status=403)
        if not self.round.completed and not self.tournament.pref('all_results_released'):
            logger.warning("Refused results for %s: round not completed", self.round.name)
            return render(request, 'public_results_not_available.html', status=403)

        # If there's a query string, store the session setting
        if request.GET.get('view') in ['team', 'debate']:
            request.session['results_view'] = request.GET['view']

            # Test saving it explicitly, if it doesn't work then prevent middlware
            # from saving it. This can happen if write permissions to the database
            # are revoked because the database has reached its row limit.
            try:
                request.session.save()
            except ProgrammingError as e:
                logger.warning("Could not save session: " + str(e))
                request.session.modified = False

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['view_type'] = self.request.session.get('results_view', self.default_view)
        return super().get_context_data(**kwargs)


# ==============================================================================
# Ballot entry form views
# ==============================================================================

class BaseBallotSetView(LogActionMixin, TournamentMixin, FormView):
    """Base class for views displaying ballot set entry forms."""

    action_log_content_object_attr = 'ballotsub'
    tabroom = False
    for_admin = False

    def get_context_data(self, **kwargs):
        kwargs['ballotsub'] = self.ballotsub
        kwargs['debate'] = self.debate
        kwargs['all_ballotsubs'] = self.get_all_ballotsubs()
        kwargs['new'] = self.relates_to_new_ballotsub
        kwargs['for_admin'] = self.for_admin

        use_team_code_names = use_team_code_names_data_entry(self.tournament, self.tabroom)
        kwargs['use_team_code_names'] = use_team_code_names

        sides = self.tournament.sides
        if use_team_code_names == 'off':
            kwargs['debate_name'] = _(" vs ").join(self.debate.get_team(side).short_name for side in sides)
        else:
            kwargs['debate_name'] = _(" vs ").join(self.debate.get_team(side).code_name for side in sides)
        kwargs['page_subtitle'] = _("%(matchup)s: %(round)s @ %(room)s") % {
            'round': self.debate.round.name,
            'room': getattr(self.debate.venue, 'display_name', _("N/A")),
            'matchup': kwargs['debate_name'],
        }

        kwargs['iron'] = self.debate.debateteam_set.annotate(iron=Count('team__debateteam__teamscore',
            filter=Q(team__debateteam__debate__round=self.debate.round.prev,
                team__debateteam__teamscore__has_ghost=True,
                team__debateteam__teamscore__ballot_submission__confirmed=True)),
        ).filter(iron__gt=0)
        if self.ballotsub.id is None:
            kwargs['current_iron'] = 0
        else:
            kwargs['current_iron'] = self.debate.debateteam_set.annotate(iron=Count('team__debateteam__teamscore',
                filter=Q(
                    team__debateteam__debate__round=self.debate.round,
                    team__debateteam__teamscore__has_ghost=True,
                    team__debateteam__teamscore__ballot_submission=self.ballotsub)),
            ).filter(iron__gt=0).count()

        return super().get_context_data(**kwargs)

    def get_all_ballotsubs(self):
        all_ballotsubs = self.debate.ballotsubmission_set.order_by('version').select_related('submitter', 'confirmer', 'motion')
        if not self.request.user.is_superuser:
            all_ballotsubs = all_ballotsubs.exclude(discarded=True)
        populate_identical_ballotsub_lists(all_ballotsubs)
        return all_ballotsubs

    def get_form_class(self):
        return {
            'DebateResultByAdjudicator': PerAdjudicatorEliminationBallotSetForm,
            'DebateResultByAdjudicatorWithScores': PerAdjudicatorBallotSetForm,
            'ConsensusDebateResult': SingleEliminationBallotSetForm,
            'ConsensusDebateResultWithScores': SingleBallotSetForm,
        }[get_class_name(self.ballotsub, self.debate.round, self.tournament)]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ballotsub'] = self.ballotsub
        return kwargs

    def add_success_message(self):
        # Default implementation does nothing.
        pass

    def should_send_email_receipts(self):
        return self.tournament.pref('enable_ballot_receipts') and not (self.debate.round.stage == Round.STAGE_ELIMINATION and
            self.tournament.pref('teams_in_debate') == 'bp')

    def matchup_description(self):
        """This is primarily shown in messages, some of which are public. This
        is slightly different to its use in templates, but should match given
        paper ballots use code names. It does however ignore the 'both' option
        in favour of just showing the code name"""
        code_opt = use_team_code_names_data_entry(self.tournament, self.tabroom)
        if code_opt == 'code' or code_opt == 'both':
            return self.debate.matchup_codes
        else:
            return self.debate.matchup

    def form_valid(self, form):
        self.ballotsub = form.save()
        if self.ballotsub.confirmed:
            self.ballotsub.confirmer = self.request.user
            self.ballotsub.confirm_timestamp = timezone.now()
            self.ballotsub.save()

            if self.should_send_email_receipts():
                async_to_sync(get_channel_layer().send)("notifications", {
                    "type": "email",
                    "message": BulkNotification.EventType.BALLOTS_CONFIRMED,
                    "extra": {"debate_id": self.debate.id},
                    "subject": self.tournament.pref("ballot_email_subject"),
                    "body": self.tournament.pref("ballot_email_message"),
                    "send_to": None,
                })

        self.add_success_message()
        self.round = form.debate.round  # for LogActionMixin

        return super().form_valid(form)

    def populate_objects(self, prefill=True):
        """Subclasses must implement this method to set `self.ballotsub` and
        `self.debate`. If it returns something other than None, its return
        value will be used as the response, bypassing ordinary template
        rendering."""
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        error_response = self.populate_objects()
        if error_response:
            return error_response
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        error_response = self.populate_objects(prefill=False)
        if error_response:
            return error_response
        return super().post(request, *args, **kwargs)


class AdministratorBallotSetMixin(AdministratorMixin):
    template_name = 'ballot_entry.html'
    tabroom = True

    def get_success_url(self):
        return reverse_round('results-round-list', self.ballotsub.debate.round)


class OldAdministratorBallotSetMixin(AdministratorMixin):
    template_name = 'enter_results.html'
    tabroom = True

    def get_success_url(self):
        return reverse_round('results-round-list', self.ballotsub.debate.round)


class AssistantBallotSetMixin(AssistantMixin):
    template_name = 'ballot_entry.html'
    tabroom = True

    def get_success_url(self):
        return reverse_tournament('results-assistant-round-list', self.tournament)


class OldAssistantBallotSetMixin(AssistantMixin):
    template_name = 'assistant_enter_results.html'
    tabroom = True

    def get_success_url(self):
        return reverse_tournament('results-assistant-round-list', self.tournament)


class BaseNewBallotSetView(SingleObjectFromTournamentMixin, BaseBallotSetView):

    model = Debate
    tournament_field_name = 'round__tournament'
    relates_to_new_ballotsub = True
    action_log_type = ActionLogEntry.ACTION_TYPE_BALLOT_CREATE
    pk_url_kwarg = 'debate_id'
    page_title = gettext_lazy("New Ballot Set")

    def add_success_message(self):
        message = _("Ballot set for %(debate)s added.") % {'debate': self.matchup_description()}
        if self.should_send_email_receipts() and self.ballotsub.confirmed:
            message += _(" Email receipts queued to be sent.")
        messages.success(self.request, message)

    def get_error_url(self):
        return self.get_success_url()

    def populate_objects(self, prefill=True):
        self.debate = self.object = self.get_object()
        self.ballotsub = BallotSubmission(debate=self.debate, submitter=self.request.user,
            submitter_type=BallotSubmission.SUBMITTER_TABROOM,
            ip_address=get_ip_address(self.request))

        if self.debate.round.ballots_per_debate == 'per-adj' and \
                not self.debate.adjudicators.has_chair:
            messages.error(self.request, _("Whoops! The debate %(debate)s doesn't have a chair, "
                "so you can't enter results for it.") % {'debate': self.matchup_description()})
            return HttpResponseRedirect(self.get_error_url())

        if not (self.tournament.pref('draw_side_allocations') == 'manual-ballot' and
                self.tournament.pref('teams_in_debate') == 'two') and not self.debate.sides_confirmed:
            messages.error(self.request, _("Whoops! The debate %(debate)s doesn't have its "
                "sides confirmed, so you can't enter results for it.") % {'debate': self.matchup_description()})
            return HttpResponseRedirect(self.get_error_url())


class AdminNewBallotSetView(AdministratorBallotSetMixin, BaseNewBallotSetView):
    pass


class AssistantNewBallotSetView(AssistantBallotSetMixin, BaseNewBallotSetView):
    pass


class OldAdminNewBallotSetView(OldAdministratorBallotSetMixin, BaseNewBallotSetView):
    pass


class OldAssistantNewBallotSetView(OldAssistantBallotSetMixin, BaseNewBallotSetView):
    pass


class BaseEditBallotSetView(SingleObjectFromTournamentMixin, BaseBallotSetView):

    model = BallotSubmission
    tournament_field_name = 'debate__round__tournament'
    relates_to_new_ballotsub = False
    page_title = gettext_lazy("Edit Ballot Set")

    def get_action_log_type(self):
        if self.ballotsub.discarded:
            return ActionLogEntry.ACTION_TYPE_BALLOT_DISCARD
        elif self.ballotsub.confirmed:
            return ActionLogEntry.ACTION_TYPE_BALLOT_CONFIRM
        return ActionLogEntry.ACTION_TYPE_BALLOT_EDIT

    def get_success_url(self):
        return reverse_round('results-round-list', self.ballotsub.debate.round)

    def add_success_message(self):
        if self.ballotsub.discarded:
            message = _("Ballot set for %(matchup)s discarded.")
        elif self.ballotsub.confirmed:
            message = _("Ballot set for %(matchup)s confirmed.")
        else:
            message = _("Edits to ballot set for %(matchup)s saved.")

        if self.should_send_email_receipts() and self.ballotsub.confirmed:
            message += _(" Email receipts queued to be sent.")

        messages.success(self.request, message % {'matchup': self.matchup_description()})

    def populate_objects(self, prefill=True):
        self.ballotsub = self.object = self.get_object()
        self.debate = self.ballotsub.debate
        self.round_motions = {}
        for rm in RoundMotion.objects.filter(round_id=self.debate.round_id):
            self.round_motions[rm.motion_id] = rm


class AdminEditBallotSetView(AdministratorBallotSetMixin, BaseEditBallotSetView):
    pass


class AssistantEditBallotSetView(AssistantBallotSetMixin, BaseEditBallotSetView):
    pass


class OldAdminEditBallotSetView(OldAdministratorBallotSetMixin, BaseEditBallotSetView):
    pass


class OldAssistantEditBallotSetView(OldAssistantBallotSetMixin, BaseEditBallotSetView):
    pass


class BasePublicNewBallotSetView(PersonalizablePublicTournamentPageMixin, RoundMixin, BaseBallotSetView):

    template_name = 'public_enter_results.html'
    relates_to_new_ballotsub = True
    action_log_type = ActionLogEntry.ACTION_TYPE_BALLOT_SUBMIT
    page_title = gettext_lazy("Enter Results")

    def get_context_data(self, **kwargs):
        kwargs['private_url'] = self.private_url
        kwargs['prefilled'] = self.prefilled
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['password'] = True
        kwargs['result'] = self.result
        kwargs['vetos'] = self.vetos
        return kwargs

    def add_success_message(self):
        messages.success(self.request, _("Thanks, %(user)s! Your ballot for %(debate)s has "
                "been recorded.") % {'user': self.object.name, 'debate': self.matchup_description()})

    def populate_objects(self, prefill=True):
        self.object = self.get_object() # must be populated before self.error_page() called

        if self.round.draw_status != Round.STATUS_RELEASED:
            return self.error_page(_("The draw for this round hasn't been released yet."))

        if (self.tournament.pref('enable_motions') or self.tournament.pref('motion_vetoes_enabled')) \
                and not self.round.motions_released:
            return self.error_page(_("The motions for this round haven't been released yet."))

        try:
            self.debateadj = DebateAdjudicator.objects.get(adjudicator=self.object, debate__round=self.round)
        except DebateAdjudicator.DoesNotExist:
            return self.error_page(_("It looks like you don't have a debate this round."))
        except DebateAdjudicator.MultipleObjectsReturned:
            return self.error_page(_("It looks like you're assigned to two or more debates this round. "
                    "Please contact a tab room official."))

        self.debate = self.debateadj.debate
        self.ballotsub = BallotSubmission(debate=self.debate, ip_address=get_ip_address(self.request),
            submitter_type=BallotSubmission.SUBMITTER_PUBLIC, single_adj=self.tournament.pref('individual_ballots'),
            private_url=self.private_url, participant_submitter=self.object)

        self.round_motions = {}
        for rm in RoundMotion.objects.filter(round_id=self.debate.round_id):
            self.round_motions[rm.motion_id] = rm

        self.result = DebateResult(self.ballotsub, round=self.round, tournament=self.tournament)

        self.vetos = None
        self.prefilled = False
        if self.ballotsub.single_adj and prefill:
            former_ballot = self.debate.ballotsubmission_set.filter(discarded=False).exclude(
                participant_submitter=self.object,
            ).prefetch_related(
                'speakerscore_set', 'speakerscore_set__debate_team',
                'debateteammotionpreference_set', 'debateteammotionpreference_set__debate_team',
            ).order_by('-confirmed', '-version').first()
            if former_ballot is not None:
                self.set_speakers(former_ballot)
                self.set_motions(former_ballot)

        if not self.debate.adjudicators.has_chair:
            return self.error_page(_("Your debate doesn't have a chair, so you can't enter results for it. "
                    "Please contact a tab room official."))

        if not (self.tournament.pref('draw_side_allocations') == 'manual-ballot' and
                self.tournament.pref('teams_in_debate') == 'two') and not self.debate.sides_confirmed:
            return self.error_page(_("It looks like the sides for this debate haven't yet been confirmed, "
                    "so you can't enter results for it. Please contact a tab room official."))

    def set_speakers(self, former_ballot):
        if former_ballot.speakerscore_set.exists():
            for ss in former_ballot.speakerscore_set.all():
                self.result.set_speaker(ss.debate_team.side, ss.position, ss.speaker)
                self.result.set_ghost(ss.debate_team.side, ss.position, ss.ghost)
            self.prefilled = True

    def set_motions(self, former_ballot):
        if self.tournament.pref('enable_motions'):
            self.ballotsub._roundmotion = self.round_motions[former_ballot.motion_id]
            self.prefilled = True
        if self.tournament.pref('motion_vetoes_enabled'):
            self.vetos = {}
            for dtmp in former_ballot.debateteammotionpreference_set.all():
                self.vetos[dtmp.debate_team.side] = dtmp
                self.vetos[dtmp.debate_team.side]._roundmotion = self.round_motions[dtmp.motion_id]
            self.prefilled = True

    def error_page(self, message):
        # This bypasses the normal TemplateResponseMixin and ContextMixin
        # machinery, to avoid loading the error page with potentially
        # confidentiality-compromising context.
        context = {'adjudicator': self.object, 'message': message}
        return self.response_class(
            request=self.request,
            template=['public_enter_results_error.html'],
            context=context,
            using=self.template_engine,
        )

    def get_all_ballotsubs(self):
        q = super().get_all_ballotsubs()
        if self.ballotsub.single_adj:
            return q.filter(participant_submitter=self.ballotsub.participant_submitter)
        return q


class OldPublicNewBallotSetByIdUrlView(SingleObjectFromTournamentMixin, BasePublicNewBallotSetView):
    model = Adjudicator
    pk_url_kwarg = 'adjudicator_pk'
    allow_null_tournament = True
    private_url = False

    def get_success_url(self):
        return reverse_tournament('post-results-public-ballotset-new', self.tournament)

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'public'


class OldPublicNewBallotSetByRandomisedUrlView(SingleObjectByRandomisedUrlMixin, BasePublicNewBallotSetView):
    model = Adjudicator
    allow_null_tournament = True
    private_url = True

    def get_success_url(self):
        return reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': self.kwargs['url_key']})

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'private-urls'


class PostPublicBallotSetSubmissionURLView(TournamentMixin, TemplateView):
    """This exists as a non-cached placeholder page that users are sent to
    after submitting a random ballot. Added because sending them back to their
    private URL brings up the same form again with a double-submission error"""

    template_name = 'base.html'


# ==============================================================================
# Other public views
# ==============================================================================

class BasePublicBallotScoresheetsView(PublicTournamentPageMixin, SingleObjectFromTournamentMixin, TemplateView):
    """Base Public view showing the ballots for a debate as scoresheets."""

    model = Debate
    public_page_preference = 'ballots_released'
    tournament_field_name = 'round__tournament'
    template_name = 'public_ballot_set.html'
    error_template_name = 'public_ballot_set_error.html'

    def matchup_description(self):
        if use_team_code_names(self.tournament, False):
            return self.object.matchup_codes
        else:
            return self.object.matchup

    def get_queryset(self):
        return self.model.objects.select_related(
            'round',
        ).prefetch_related('debateteam_set__team')

    def response_error(self, error):
        status, message = error
        return self.response_class(
            request=self.request,
            template=[self.error_template_name],
            context={'message': message},
            using=self.template_engine,
            status=status,
        )

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except self.model.MultipleObjectsReturned:
            error = (500, _("It looks like you were assigned to two or more debates. Please contact a tab room official."))
        else:
            error = self.check_permissions()

        if error:
            return self.response_error(error)

        return super().get(self, request, *args, **kwargs)


class PublicBallotScoresheetsView(BasePublicBallotScoresheetsView):
    """Public view showing the confirmed ballots for a debate as scoresheets."""

    def check_permissions(self):
        debate = self.object
        round = debate.round
        if round.silent and not round.tournament.pref('all_results_released'):
            logger.warning("Refused public view of ballots for %s: %s is silent", debate, round.name)
            return 403, _("This debate is in %s, which is a silent round.") % round.name
        if not round.completed and not round.tournament.pref('all_results_released'):
            logger.warning("Refused public view of ballots for %s: %s is not completed", debate, round.name)
            return 403, _("This debate is in %s, the results for which aren't available yet.") % round.name

        if debate.result_status != Debate.STATUS_CONFIRMED:
            logger.warning("Refused public view of ballots for %s: not confirmed", debate)
            return 404, _("The result for debate %s is not confirmed.") % self.matchup_description()
        if debate.confirmed_ballot is None:
            logger.warning("Refused public view of ballots for %s: no confirmed ballot", debate)
            return 404, _("The debate %s does not have a confirmed ballot.") % self.matchup_description()

    def get_context_data(self, **kwargs):
        kwargs['motion'] = self.object.confirmed_ballot.motion or self.object.round.motion_set.first()
        kwargs['result'] = self.object.confirmed_ballot.result
        kwargs['use_code_names'] = use_team_code_names(self.tournament, False)
        return super().get_context_data(**kwargs)


class AdjudicatorPrivateUrlBallotScoresheetView(RoundMixin, SingleObjectByRandomisedUrlMixin, BasePublicBallotScoresheetsView):

    template_name = 'privateurl_ballot_set.html'
    error_template_name = 'privateurl_ballot_set_error.html'
    slug_url_kwarg = 'url_key'
    slug_field = 'debateadjudicator__adjudicator__url_key'

    def is_page_enabled(self, tournament):
        return True

    def check_permissions(self):
        if not self.object.ballotsubmission_set.filter(discarded=False).exists():
            logger.warning("Refused public view of ballots for %s: no ballot", self.object)
            return 404, _("There is no result yet for debate %s.") % self.matchup_description()

    def get_context_data(self, **kwargs):
        ballot = self.object.ballotsubmission_set.filter(discarded=False).order_by('version').last()
        kwargs['motion'] = ballot.motion
        kwargs['result'] = ballot.result
        kwargs['use_code_names'] = use_team_code_names(self.tournament, False)
        kwargs['adjudicator'] = Adjudicator.objects.get(url_key=self.kwargs.get('url_key'))
        return super().get_context_data(**kwargs)

    def response_error(self, error):
        status, message = error
        return self.response_class(
            request=self.request,
            template=[self.error_template_name],
            context={'message': message, 'adjudicator': Adjudicator.objects.get(url_key=self.kwargs.get('url_key'))},
            using=self.template_engine,
            status=status,
        )

    def get_queryset(self):
        return super().get_queryset().filter(round=self.round)


class SpeakerPrivateUrlBallotScoresheetView(RoundMixin, SingleObjectByRandomisedUrlMixin, PublicBallotScoresheetsView):
    slug_field = 'debateteam__team__speaker__url_key'
    public_page_preference = 'private_ballots_released'

    def is_page_enabled(self, tournament):
        return True

    def get_queryset(self):
        return super().get_queryset().filter(round=self.round)


class PublicBallotSubmissionIndexView(PublicTournamentPageMixin, RoundMixin, VueTableTemplateView):
    """Public view listing all debate-adjudicators for the current round, as
    links for them to enter their ballots."""

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'public'

    def is_draw_released(self):
        return self.round.draw_status == Round.STATUS_RELEASED and self.round.motions_good_for_public

    def get_template_names(self):
        if self.is_draw_released():
            return ['public_add_ballot.html']
        else:
            return ['public_add_ballot_unreleased.html']

    def get_table(self):
        if not self.is_draw_released():
            return None

        debateadjs = DebateAdjudicator.objects.filter(
            debate__round=self.round,
        ).select_related(
            'adjudicator', 'debate__venue',
        ).prefetch_related(
            'debate__venue__venuecategory_set',
        ).order_by('adjudicator__name')

        table = TabbycatTableBuilder(view=self, sort_key='adj')

        data = [{
            'text': _("Add result from %(adjudicator)s") % {'adjudicator': escape(da.adjudicator.get_public_name(self.tournament))},
            'link': reverse_round('old-results-public-ballotset-new-pk', self.round,
                    kwargs={'adjudicator_pk': da.adjudicator_id}),
        } for da in debateadjs]
        header = {'key': 'adj', 'title': _("Adjudicator")}
        table.add_column(header, data)

        debates = [da.debate for da in debateadjs]
        table.add_debate_venue_columns(debates)
        return table


class PostponeDebateView(AdministratorMixin, RoundMixin, PostOnlyRedirectView):

    round_redirect_pattern_name = 'results-round-list'

    def post(self, request, *args, **kwargs):
        debate = Debate.objects.get(id=kwargs.pop('debate_id'))
        debate.result_status = Debate.STATUS_POSTPONED
        debate.save()

        # Notify the Results Page
        group_name = BallotStatusConsumer.group_prefix + "_" + debate.round.tournament.slug
        meta = get_status_meta(debate)
        async_to_sync(get_channel_layer().group_send)(group_name, {
            "type": "send_json",
            "data": {
                'status': debate.result_status,
                'icon': meta[0],
                'class': meta[1],
                'sort': meta[2],
                'ballot': None,
                'round': debate.round_id,
            },
        })

        return super().post(request, *args, **kwargs)


class BaseMergeLatestBallotsView(BaseNewBallotSetView):
    tabroom = True
    page_title = gettext_lazy("Merge Ballots")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['result'] = self.result
        kwargs['vetos'] = self.vetos
        kwargs['filled'] = True
        return kwargs

    def populate_objects(self, prefill=True):
        super().populate_objects()
        use_code_names = use_team_code_names_data_entry(self.tournament, True)
        self.round = self.debate.round

        bses = BallotSubmission.objects.filter(
            debate=self.debate, participant_submitter__isnull=False, discarded=False, single_adj=True,
        ).distinct('participant_submitter').select_related('participant_submitter').order_by('participant_submitter', '-version')
        populate_results(bses, self.tournament)
        self.merged_ballots = bses

        # Handle result conflicts
        self.result = DebateResult(self.ballotsub, tournament=self.tournament)
        try:
            self.result.populate_from_merge(*[b.result for b in bses])
        except ResultError as e:
            msg, t, adj, bs, side, speaker = e.args
            args = {
                'ballot_url': reverse_tournament(self.edit_ballot_url, self.tournament, kwargs={'pk': bs.id}),
                'adjudicator': adj.name,
                'speaker': speaker.name,
                'team': team_name_for_data_entry(self.debate.get_team(side), use_code_names),
            }
            if t == 'speaker':
                msg = _("The speaking order in the ballots is inconsistent, so could not be merged.")
            elif t == 'ghost':
                msg = _("Duplicate speeches are marked inconsistently, so could not be merged.")
            msg += _(" This error was caught in <a href='%(ballot_url)s'>%(adjudicator)s's ballot</a> for %(speaker)s (%(team)s).")
            messages.error(self.request, msg % args)
            return HttpResponseRedirect(self.get_list_url())

        # Handle motion conflicts
        bs_motions = BallotSubmission.objects.filter(
            id__in=[b.id for b in bses], motion__isnull=False,
        ).prefetch_related('debateteammotionpreference_set__debate_team')
        if self.tournament.pref('enable_motions'):
            try:
                merge_motions(self.ballotsub, bs_motions)
            except ValidationError as e:
                messages.error(self.request, e)
                return HttpResponseRedirect(self.get_list_url())

        # Vetos
        try:
            self.vetos = merge_motion_vetos(self.ballotsub, bs_motions)
        except ValidationError as e:
            messages.error(self.request, e)
            return HttpResponseRedirect(self.get_list_url())

    def get_all_ballotsubs(self):
        q = super().get_all_ballotsubs()
        merged = {b.id for b in self.merged_ballots}
        for b in q:
            b.merged = b.id in merged
        return q


class AdminMergeLatestBallotsView(OldAdministratorBallotSetMixin, BaseMergeLatestBallotsView):
    edit_ballot_url = 'results-ballotset-edit'
    for_admin = True

    def get_list_url(self):
        return reverse_round('results-round-list', self.round)


class AssistantMergeLatestBallotsView(OldAssistantBallotSetMixin, BaseMergeLatestBallotsView):
    edit_ballot_url = 'results-assistant-ballotset-edit'
    for_admin = False

    def get_list_url(self):
        return reverse_tournament('results-assistant-round-list', self.tournament)
