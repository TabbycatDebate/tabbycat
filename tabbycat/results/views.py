import datetime
import logging

from django.contrib import messages
from django.db import ProgrammingError
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import FormView, TemplateView, View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from draw.prefetch import populate_opponents
from participants.models import Adjudicator
from tournaments.mixins import (CurrentRoundMixin, PublicTournamentPageMixin, RoundMixin,
                                SingleObjectByRandomisedUrlMixin, SingleObjectFromTournamentMixin,
                                TournamentMixin)
from tournaments.models import Round
from utils.misc import get_ip_address, redirect_round, reverse_round, reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin, CacheMixin
from utils.views import JsonDataResponsePostView, VueTableTemplateView
from utils.tables import TabbycatTableBuilder
from venues.models import Venue

from .forms import BPEliminationResultForm, PerAdjudicatorBallotSetForm, SingleBallotSetForm
from .models import BallotSubmission, TeamScore
from .tables import ResultsTableBuilder
from .prefetch import populate_confirmed_ballots
from .utils import ballot_checkin_number_left, get_result_status_stats, populate_identical_ballotsub_lists

logger = logging.getLogger(__name__)


class PublicResultsIndexView(PublicTournamentPageMixin, TemplateView):

    template_name = 'public_results_index.html'
    public_page_preference = 'public_results'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs["rounds"] = tournament.round_set.filter(
            seq__lt=tournament.current_round.seq,
            silent=False).order_by('seq')
        return super().get_context_data(**kwargs)


# ==============================================================================
# Views that show the results for all rounds in a debate
# ==============================================================================

class BaseResultsEntryForRoundView(RoundMixin, VueTableTemplateView):

    def _get_draw(self):
        if not hasattr(self, '_draw'):
            self._draw = self.get_round().debate_set_with_prefetches(
                    ordering=('room_rank',), results=True, wins=True)
        return self._draw

    def get_table(self):
        draw = self._get_draw()
        table = ResultsTableBuilder(view=self, sort_key=_("Status"))
        table.add_ballot_status_columns(draw)
        table.add_ballot_entry_columns(draw)
        table.add_debate_venue_columns(draw, for_admin=True)
        table.add_debate_results_columns(draw)
        table.add_debate_adjudicators_column(draw, show_splits=True)
        return table

    def get_context_data(self, **kwargs):
        round = self.get_round()
        result_status_stats = get_result_status_stats(round)

        kwargs["stats"] = {
            'none': result_status_stats[Debate.STATUS_NONE],
            'ballot_in': result_status_stats['B'],
            'draft': result_status_stats[Debate.STATUS_DRAFT],
            'confirmed': result_status_stats[Debate.STATUS_CONFIRMED],
            'postponed': result_status_stats[Debate.STATUS_POSTPONED],
            'total': len(self._get_draw())
        }

        return super().get_context_data(**kwargs)


class AssistantResultsEntryView(AssistantMixin, CurrentRoundMixin, BaseResultsEntryForRoundView):
    template_name = 'assistant_results.html'


class AdminResultsEntryForRoundView(AdministratorMixin, BaseResultsEntryForRoundView):
    template_name = 'admin_results.html'


class PublicResultsForRoundView(RoundMixin, PublicTournamentPageMixin, VueTableTemplateView):

    template_name = "public_results_for_round.html"
    public_page_preference = 'public_results'
    page_title = ugettext_lazy("Results")
    page_emoji = '💥'
    default_view = 'team'

    def get_table(self):
        view_type = self.request.session.get('results_view', self.default_view)
        if view_type == 'debate':
            return self.get_table_by_debate()
        else:
            return self.get_table_by_team()

    def get_table_by_debate(self):
        round = self.get_round()
        tournament = self.get_tournament()
        debates = round.debate_set_with_prefetches(results=True, wins=True)
        populate_confirmed_ballots(debates, motions=True,
                results=tournament.pref('ballots_per_debate') == 'per-adj')

        table = TabbycatTableBuilder(view=self, sort_key=_("Venue"))
        table.add_debate_venue_columns(debates)
        table.add_debate_results_columns(debates)
        if not (tournament.pref('teams_in_debate') == 'bp' and round.is_break_round):
            table.add_debate_ballot_link_column(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if tournament.pref('show_motions_in_results'):
            table.add_debate_motion_column(debates)

        return table

    def get_table_by_team(self):
        round = self.get_round()
        tournament = self.get_tournament()
        teamscores = TeamScore.objects.filter(debate_team__debate__round=round,
                ballot_submission__confirmed=True).prefetch_related(
                'debate_team__team__speaker_set', 'debate_team__team__institution',
                'debate_team__debate__debateadjudicator_set__adjudicator',
                'debate_team__debate__debateteam_set__team',
                'debate_team__debate__round').select_related('ballot_submission')
        debates = [ts.debate_team.debate for ts in teamscores]

        if tournament.pref('teams_in_debate') == 'two':
            populate_opponents([ts.debate_team for ts in teamscores])
        populate_confirmed_ballots(debates, motions=True,
                results=tournament.pref('ballots_per_debate') == 'per-adj')

        table = TabbycatTableBuilder(view=self, sort_key=_("Team"))
        table.add_team_columns([ts.debate_team.team for ts in teamscores])
        table.add_debate_result_by_team_column(teamscores)
        table.add_debate_side_by_team_column(teamscores)
        if not (tournament.pref('teams_in_debate') == 'bp' and round.is_break_round):
            table.add_debate_ballot_link_column(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if tournament.pref('show_motions_in_results'):
            table.add_debate_motion_column(debates)

        return table

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        round = self.get_round()
        if round.silent and not tournament.pref('all_results_released'):
            logger.warning("Refused results for %s: silent", round.name)
            return render(request, 'public_results_silent.html')
        if round.seq >= tournament.current_round.seq and not tournament.pref('all_results_released'):
            logger.warning("Refused results for %s: not yet available", round.name)
            return render(request, 'public_results_not_available.html')

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
# Views that update the debate status (only)
# ==============================================================================

class BaseUpdateDebateStatusView(AdministratorMixin, RoundMixin, View):

    def post(self, request, *args, **kwargs):
        debate_id = request.POST['debate_id']
        try:
            debate = Debate.objects.get(round=self.get_round(), id=debate_id)
        except Debate.DoesNotExist:
            return HttpResponseBadRequest("Error: There isn't a debate in %s with id %d." % (self.get_round().name, debate_id))
        debate.result_status = self.new_status
        debate.save()
        return redirect_round('results-round-list', debate.round)


class PostponeDebateView(BaseUpdateDebateStatusView):
    new_status = Debate.STATUS_POSTPONED


class UnpostponeDebateView(BaseUpdateDebateStatusView):
    new_status = Debate.STATUS_NONE


# ==============================================================================
# Ballot entry form views
# ==============================================================================

class BaseBallotSetView(LogActionMixin, TournamentMixin, FormView):
    """Base class for views displaying ballot set entry forms."""

    action_log_content_object_attr = 'ballotsub'

    def get_context_data(self, **kwargs):
        kwargs['ballotsub'] = self.ballotsub
        kwargs['debate'] = self.debate
        kwargs['all_ballotsubs'] = self.get_all_ballotsubs()
        kwargs['new'] = self.relates_to_new_ballotsub
        return super().get_context_data(**kwargs)

    def get_all_ballotsubs(self):
        all_ballotsubs = self.debate.ballotsubmission_set.order_by('version').select_related('submitter', 'confirmer', 'motion')
        if not self.request.user.is_superuser:
            all_ballotsubs = all_ballotsubs.exclude(discarded=True)
        populate_identical_ballotsub_lists(all_ballotsubs)
        return all_ballotsubs

    def get_form_class(self):
        tournament = self.get_tournament()
        if tournament.pref('teams_in_debate') == 'bp' and self.debate.round.is_break_round:
            return BPEliminationResultForm
        elif tournament.pref('ballots_per_debate') == 'per-adj':
            return PerAdjudicatorBallotSetForm
        else:
            return SingleBallotSetForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ballotsub'] = self.ballotsub
        return kwargs

    def add_success_message(self):
        # Default implementation does nothing.
        pass

    def form_valid(self, form):
        self.ballotsub = form.save()
        if self.ballotsub.confirmed:
            self.ballotsub.confirmer = self.request.user
            self.ballotsub.confirm_timestamp = datetime.datetime.now()
            self.ballotsub.save()
        self.add_success_message()
        self.round = self.ballotsub.debate.round  # for LogActionMixin
        return super().form_valid(form)

    def populate_objects(self):
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
        error_response = self.populate_objects()
        if error_response:
            return error_response
        return super().post(request, *args, **kwargs)


class AdministratorBallotSetMixin(AdministratorMixin):
    template_name = 'enter_results.html'

    def get_success_url(self):
        return reverse_round('results-round-list', self.ballotsub.debate.round)


class AssistantBallotSetMixin(AssistantMixin):
    template_name = 'assistant_enter_results.html'

    def get_success_url(self):
        return reverse_tournament('results-assistant-round-list', self.get_tournament())


class BaseNewBallotSetView(SingleObjectFromTournamentMixin, BaseBallotSetView):

    model = Debate
    tournament_field_name = 'round__tournament'
    relates_to_new_ballotsub = True
    action_log_type = ActionLogEntry.ACTION_TYPE_BALLOT_CREATE
    pk_url_kwarg = 'debate_id'

    def add_success_message(self):
        messages.success(self.request, _("Ballot set for %(debate)s added.") % {'debate': self.debate.matchup})

    def get_error_url(self):
        return self.get_success_url()

    def populate_objects(self):
        self.debate = self.object = self.get_object()
        self.ballotsub = BallotSubmission(debate=self.debate, submitter=self.request.user,
            submitter_type=BallotSubmission.SUBMITTER_TABROOM,
            ip_address=get_ip_address(self.request))

        t = self.get_tournament()

        if t.pref('ballots_per_debate') == 'per-adj' and \
                not self.debate.adjudicators.has_chair:
            messages.error(self.request, _("Whoops! The debate %(debate)s doesn't have a chair, "
                "so you can't enter results for it.") % {'debate': self.debate.matchup})
            return HttpResponseRedirect(self.get_error_url())

        if not (t.pref('draw_side_allocations') == 'manual-ballot' and
                t.pref('teams_in_debate') == 'two') and not self.debate.sides_confirmed:
            messages.error(self.request, _("Whoops! The debate %(debate)s doesn't have its "
                "sides confirmed, so you can't enter results for it.") % {'debate': self.debate.matchup})
            return HttpResponseRedirect(self.get_error_url())


class AdminNewBallotSetView(AdministratorBallotSetMixin, BaseNewBallotSetView):
    pass


class AssistantNewBallotSetView(AssistantBallotSetMixin, BaseNewBallotSetView):
    pass


class BaseEditBallotSetView(SingleObjectFromTournamentMixin, BaseBallotSetView):

    model = BallotSubmission
    tournament_field_name = 'debate__round__tournament'
    relates_to_new_ballotsub = False

    def get_action_log_type(self):
        if self.ballotsub.discarded:
            return ActionLogEntry.ACTION_TYPE_BALLOT_DISCARD
        elif self.ballotsub.confirmed:
            return ActionLogEntry.ACTION_TYPE_BALLOT_CONFIRM
        else:
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
        messages.success(self.request, message % {'matchup': self.debate.matchup})

    def populate_objects(self):
        self.ballotsub = self.object = self.get_object()
        self.debate = self.ballotsub.debate


class AdminEditBallotSetView(AdministratorBallotSetMixin, BaseEditBallotSetView):
    pass


class AssistantEditBallotSetView(AssistantBallotSetMixin, BaseEditBallotSetView):
    pass


class BasePublicNewBallotSetView(PublicTournamentPageMixin, BaseBallotSetView):

    template_name = 'public_enter_results.html'
    relates_to_new_ballotsub = True
    action_log_type = ActionLogEntry.ACTION_TYPE_BALLOT_SUBMIT

    def get_context_data(self, **kwargs):
        kwargs['private_url'] = self.private_url
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['password'] = True
        return kwargs

    def add_success_message(self):
        messages.success(self.request, _("Thanks, %(user)s! Your ballot for %(debate)s has "
                "been recorded.") % {'user': self.object.name, 'debate': self.debate.matchup})

    def get_success_url(self):
        return reverse_tournament('post-results-public-ballotset-new', self.get_tournament())

    def populate_objects(self):
        self.object = self.get_object() # must be populated before self.error_page() called

        tournament = self.get_tournament()
        round = tournament.current_round
        if round.draw_status != Round.STATUS_RELEASED:
            return self.error_page(_("The draw for this round hasn't been released yet."))

        if (tournament.pref('enable_motions') or tournament.pref('motion_vetoes_enabled')) \
                and not round.motions_released:
            return self.error_page(_("The motions for this round haven't been released yet."))

        try:
            self.debateadj = DebateAdjudicator.objects.get(adjudicator=self.object, debate__round=round)
        except DebateAdjudicator.DoesNotExist:
            return self.error_page(_("It looks like you don't have a debate this round."))
        except DebateAdjudicator.MultipleObjectsReturned:
            return self.error_page(_("It looks like you're assigned to two or more debates this round. "
                    "Please contact a tab room official."))

        self.debate = self.debateadj.debate
        self.ballotsub = BallotSubmission(debate=self.debate, ip_address=get_ip_address(self.request),
            submitter_type=BallotSubmission.SUBMITTER_PUBLIC)

        if not self.debate.adjudicators.has_chair:
            return self.error_page(_("Your debate doesn't have a chair, so you can't enter results for it. "
                    "Please contact a tab room official."))

        if not (tournament.pref('draw_side_allocations') == 'manual-ballot' and
                tournament.pref('teams_in_debate') == 'two') and not self.debate.sides_confirmed:
            return self.error_page(_("It looks like the sides for this debate haven't yet been confirmed, "
                    "so you can't enter results for it. Please contact a tab room official."))

    def error_page(self, message):
        # This bypasses the normal TemplateResponseMixin and ContextMixin
        # machinery, to avoid loading the error page with potentially
        # confidentiality-compromising context.
        context = {'adjudicator': self.object, 'message': message}
        return self.response_class(
            request=self.request,
            template='public_enter_results_error.html',
            context=context,
            using=self.template_engine
        )


class PublicNewBallotSetByIdUrlView(SingleObjectFromTournamentMixin, BasePublicNewBallotSetView):
    model = Adjudicator
    pk_url_kwarg = 'adj_id'
    allow_null_tournament = True
    private_url = False

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'public'


class PublicNewBallotSetByRandomisedUrlView(SingleObjectByRandomisedUrlMixin, BasePublicNewBallotSetView):
    model = Adjudicator
    allow_null_tournament = True
    private_url = True

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'private-urls'


class PostPublicBallotSetSubmissionURLView(TournamentMixin, TemplateView):
    """This exists as a non-cached placeholder page that users are sent to
    after submitting a random ballot. Added because sending them back to their
    private URL brings up the same form again with a double-submission error"""

    template_name = 'base.html'


# ==============================================================================
# Ballot check-in views
# ==============================================================================

class DebateBallotCheckinError(Exception):
    pass


class BallotCheckinView(AssistantMixin, RoundMixin, TemplateView):
    template_name = 'ballot_checkin.html'

    def get_page_subtitle(self):
        """Override RoundMixin to allow template subtitle to take precedence."""
        return ""

    def get_context_data(self, **kwargs):
        kwargs['ballots_left'] = ballot_checkin_number_left(self.get_round())
        venues = Venue.objects.filter(debate__round=self.get_round(),
                debate__ballot_in=False)
        kwargs['venue_options'] = venues

        return super().get_context_data(**kwargs)


class BaseBallotCheckinJsonResponseView(AssistantMixin, RoundMixin, JsonDataResponsePostView):

    def get_debate(self):
        venue_id = self.request.POST.get('venue')

        if venue_id is None:
            raise DebateBallotCheckinError(_("There aren't any venues with that name."))

        # TODO: The below errors are all hangovers from when searches were by
        # name only. They can still in theory happen, if an administrator
        # changes things (e.g. deletes or reassigns a venue) and the client
        # doesn't reload the page, so that the client is working on outdated
        # information. Nonetheless, this workflow needs to be reworked for the
        # new paradigm of selecting venues from a predefined list, while keeping
        # the UI textbox-centric.

        try:
            venue = Venue.objects.get(id=venue_id)
        except Venue.DoesNotExist:
            raise DebateBallotCheckinError(_("There aren't any venues with that name."))

        try:
            debate = Debate.objects.get(round=self.get_round(), venue=venue)
        except Debate.DoesNotExist:
            raise DebateBallotCheckinError(_("There wasn't a debate in venue %(venue_name)s "
                "this round.") % {'venue_name': venue.name})
        except Debate.MultipleObjectsReturned:
            raise DebateBallotCheckinError(_("There appear to be multiple debates in venue "
                "%(venue_name)s this round.") % {'venue_name': venue.name})

        if debate.ballot_in:
            raise DebateBallotCheckinError(_("The ballot for venue %(venue_name)s has already "
                "been checked in.") % {'venue_name': venue.name})

        return debate


class BallotCheckinGetDetailsView(BaseBallotCheckinJsonResponseView):

    def post_data(self):
        try:
            debate = self.get_debate()
        except DebateBallotCheckinError as e:
            return {'exists': False, 'message': str(e)}

        return {
            'exists': True,
            'venue': debate.venue.name,
            'venue_id': debate.venue.id,
            'teams': [team.short_name for team in debate.teams],
            'num_adjs': len(debate.adjudicators),
            'adjudicators': [adj.name for adj in debate.adjudicators.voting()],
            'ballots_left': ballot_checkin_number_left(self.get_round()),
        }


class PostBallotCheckinView(LogActionMixin, BaseBallotCheckinJsonResponseView):

    action_log_type = ActionLogEntry.ACTION_TYPE_BALLOT_CHECKIN
    action_log_content_object_attr = 'debate'

    def post_data(self):
        try:
            self.debate = self.get_debate()
        except DebateBallotCheckinError as e:
            return {'success': False, 'message': str(e)}

        self.debate.ballot_in = True
        self.debate.save()

        self.log_action()

        return {
            'success': True,
            'venue': self.debate.venue.name,
            'matchup': self.debate.matchup,
            'ballots_left': ballot_checkin_number_left(self.get_round()),
        }


# ==============================================================================
# Other public views
# ==============================================================================

class PublicBallotScoresheetsView(CacheMixin, PublicTournamentPageMixin, SingleObjectFromTournamentMixin, TemplateView):
    """Public view showing the confirmed ballots for a debate as scoresheets."""

    model = Debate
    public_page_preference = 'ballots_released'
    tournament_field_name = 'round__tournament'
    template_name = 'public_ballot_set.html'

    def get_object(self):
        debate = super().get_object()

        round = debate.round
        if round.silent and not round.tournament.pref('all_results_released'):
            logger.warning("Refused public view of ballots for %s: %s is silent", debate, round.name)
            raise Http404("This debate is in %s, which is a silent round." % round.name)
        if round.seq >= round.tournament.current_round.seq and not round.tournament.pref('all_results_released'):
            logger.warning("Refused public view of ballots for %s: %s results not yet available", debate, round.name)
            raise Http404("This debate is in %s, the results for which aren't available yet." % round.name)

        if debate.result_status != Debate.STATUS_CONFIRMED:
            logger.warning("Refused public view of ballots for %s: not confirmed", debate)
            raise Http404("The result for debate %s is not confirmed." % debate.matchup)
        if debate.confirmed_ballot is None:
            logger.warning("Refused public view of ballots for %s: no confirmed ballot", debate)
            raise Http404("The debate %s does not have a confirmed ballot." % debate.matchup)

        return debate

    def get_context_data(self, **kwargs):
        kwargs['motion'] = self.object.confirmed_ballot.motion
        kwargs['result'] = self.object.confirmed_ballot.result
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(self, request, *args, **kwargs)


class PublicBallotSubmissionIndexView(CacheMixin, PublicTournamentPageMixin, TemplateView):
    """Public view listing all debate-adjudicators for the current round, as
    links for them to enter their ballots."""

    def is_page_enabled(self, tournament):
        return tournament.pref('participant_ballots') == 'public'

    def is_draw_released(self):
        round = self.get_tournament().current_round
        return round.draw_status == Round.STATUS_RELEASED and round.motions_good_for_public

    def get_template_names(self):
        if self.is_draw_released():
            return ['public_add_ballot.html']
        else:
            return ['public_add_ballot_unreleased.html']

    def get_context_data(self, **kwargs):
        if self.is_draw_released():
            kwargs['das'] = DebateAdjudicator.objects.filter(
                debate__round=self.get_tournament().current_round).select_related('adjudicator', 'debate').order_by('adjudicator__name')
        return super().get_context_data(**kwargs)
