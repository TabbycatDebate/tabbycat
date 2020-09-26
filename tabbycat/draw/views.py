import datetime
import logging
import unicodedata
from itertools import product

from django.conf import settings
from django.contrib import messages
from django.db.models import OuterRef, Subquery
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy, ngettext
from django.views.generic.base import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from adjallocation.utils import adjudicator_conflicts_display
from availability.utils import annotate_availability
from draw.generator.powerpair import PowerPairedDrawGenerator
from notifications.models import BulkNotification
from notifications.views import RoundTemplateEmailCreateView
from options.preferences import BPPositionCost
from participants.models import Adjudicator, Speaker, Team
from participants.prefetch import populate_win_counts
from participants.utils import get_side_history
from standings.base import StandingsError
from standings.teams import TeamStandingsGenerator
from standings.views import BaseStandingsView
from tournaments.mixins import (CurrentRoundMixin, DebateDragAndDropMixin,
    OptionalAssistantTournamentPageMixin, PublicTournamentPageMixin, RoundMixin,
    TournamentMixin)
from tournaments.models import Round
from tournaments.utils import get_side_name
from utils.misc import reverse_round, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import PostOnlyRedirectView, VueTableTemplateView
from venues.allocator import allocate_venues
from venues.models import VenueConstraint
from venues.utils import venue_conflicts_display

from .dbutils import delete_round_draw
from .generator import DrawFatalError, DrawUserError
from .manager import DrawManager
from .models import Debate, TeamSideAllocation
from .prefetch import populate_history
from .serializers import EditDebateTeamsDebateSerializer, EditDebateTeamsTeamSerializer
from .tables import (AdminDrawTableBuilder, PositionBalanceReportDrawTableBuilder,
        PositionBalanceReportSummaryTableBuilder, PublicDrawTableBuilder)

logger = logging.getLogger(__name__)


class BaseDisplayDrawTableView(TournamentMixin, VueTableTemplateView):
    """Base class for views showing a draw table to the public in some way.
    Subclasses are *not* necessarily public views; they may be admin/assistant
    views intended to facilitate displaying the draw in the general assembly
    room. Since, whether a public, assistant or admin view, the content on it
    is intended for consumption by the public, the table is always built as if
    it were a public view."""

    template_name = 'draw_display_by.html'
    sort_key = 'venue'
    page_emoji = '👏'
    empty_table_title = gettext_lazy("No debates in this round")

    @property
    def rounds(self):
        raise NotImplementedError  # leave for subclasses

    def get_page_title(self):
        if len(self.rounds) == 1:
            return _("Draw for %(round)s") % {'round': self.rounds[0].name}
        else:
            return _("Draws for Current Rounds")

    def get_page_subtitle(self):
        if len(self.rounds) == 1 and getattr(self.rounds[0], 'starts_at', None):
            return _("debates start at %(time)s (in %(time_zone)s)") % {
                     'time': self.rounds[0].starts_at.strftime('%H:%M'),
                     'time_zone': settings.TIME_ZONE}
        elif any(getattr(r, 'starts_at', None) for r in self.rounds):
            return _("start times in time zone: %(time_zone)s") % {'time_zone': settings.TIME_ZONE}
        else:
            return ""

    def populate_table(self, debates, table, highlight=[]):
        table.add_debate_venue_columns(debates)
        table.add_debate_team_columns(debates, highlight)
        table.add_debate_adjudicators_column(debates, show_splits=False)

    @classmethod
    def get_debates_for_round(cls, round):
        """Not used if the `get_debates()` method is defined. Overridden by
        `PublicDrawMixin` to blank the table if the round hasn't been
        released."""
        return round.debate_set_with_prefetches()

    def get_tables(self):

        # If the view has debates specified specifically, use those in a single table
        if hasattr(self, 'get_debates'):
            table = PublicDrawTableBuilder(view=self, sort_key=self.sort_key,
                    admin=False, empty_title=self.empty_table_title)
            self.populate_table(self.get_debates(), table)
            return [table]

        # If there's only one round, use that in a single table
        if len(self.rounds) == 1:
            table = PublicDrawTableBuilder(view=self, sort_key=self.sort_key,
                    admin=False, empty_title=self.empty_table_title)
            debates = self.get_debates_for_round(self.rounds[0])
            self.populate_table(debates, table)
            return [table]

        tables = []
        for r in self.tournament.current_rounds:
            debates = self.get_debates_for_round(r)
            if r.starts_at:
                subtitle = ngettext(
                    "debate starts at %(time)s",
                    "debates start at %(time)s",
                    debates.count(),
                ) % {'round_name': r.name, 'time': r.starts_at.strftime('%H:%M')}
            else:
                subtitle = ""
            table = PublicDrawTableBuilder(view=self, sort_key=self.sort_key,
                admin=False, title=r.name, subtitle=subtitle,
                empty_title=self.empty_table_title)
            self.populate_table(debates, table)
            tables.append(table)

        return tables


class BaseDisplayDrawForSpecificRoundTableView(RoundMixin, BaseDisplayDrawTableView):

    @property
    def rounds(self):
        return [self.round]

    def get_page_subtitle(self):
        # Skip the RoundMixin implementation
        return BaseDisplayDrawTableView.get_page_subtitle(self)

    def get_context_data(self, **kwargs):
        kwargs["round"] = self.round
        return super().get_context_data(**kwargs)


class BaseDisplayDrawForCurrentRoundsTableView(BaseDisplayDrawTableView):

    tables_orientation = 'rows'

    @property
    def rounds(self):
        return self.tournament.current_rounds


# ==============================================================================
# Viewing Draw (Public)
# ==============================================================================


class PublicDrawMixin(PublicTournamentPageMixin):
    """Governs permissions, particularly those relating to draw release."""

    empty_table_title = gettext_lazy("The draw for this round hasn't been released.")

    @cached_property
    def draws_available(self):
        return any(r.draw_status == Round.STATUS_RELEASED for r in self.rounds)

    @classmethod
    def get_debates_for_round(cls, round):
        if round.draw_status != Round.STATUS_RELEASED:
            return Debate.objects.none()
        return super().get_debates_for_round(round)

    def get_template_names(self):
        if not self.draws_available:
            return ['draw_not_released.html']
        return super().get_template_names()

    def get_tables(self):
        if not self.draws_available:
            return []
        return super().get_tables()

    def get_page_emoji(self):
        if not self.draws_available:
            return '😴'
        return super().get_page_emoji()

    def get_page_subtitle(self):
        if not self.draws_available:
            return ""
        return super().get_page_subtitle()


class PublicDrawForRoundView(PublicDrawMixin, BaseDisplayDrawForSpecificRoundTableView):

    def is_page_enabled(self, tournament):
        return tournament.pref('public_draw') == 'all-released'


class PublicDrawForCurrentRoundsView(PublicDrawMixin, BaseDisplayDrawForCurrentRoundsTableView):

    def is_page_enabled(self, tournament):
        return tournament.pref('public_draw') == 'current'


class PublicAllDrawsAllTournamentsView(PublicTournamentPageMixin, BaseDisplayDrawTableView):
    public_page_preference = 'enable_mass_draws'

    @property
    def rounds(self):
        return []

    def get_page_title(self):
        return _("All Debates for All Rounds of %(tournament)s") % {'tournament': self.tournament.name}

    def get_page_subtitle(self):
        return None

    def get_page_emoji(self):
        return None

    def populate_table(self, debates, table, highlight=[]):
        table.add_round_column(d.round for d in debates)
        super().populate_table(debates, table, highlight=highlight)

    def get_draw(self):
        all_rounds = Round.objects.filter(tournament=self.tournament,
                                          draw_status=Round.STATUS_RELEASED)
        draw = []
        for round in all_rounds:
            draw.extend(round.debate_set_with_prefetches())
        return draw


# ==============================================================================
# Viewing Draw (Briefing Room)
# ==============================================================================

class BriefingRoomDrawTableMixin:
    """Mixin for views that get projected in the briefing room, to be accessed
    only by admins and assistants."""

    def get_context_data(self, **kwargs):
        kwargs['no_popovers'] = True
        return super().get_context_data(**kwargs)


class BriefingRoomDrawByVenueTableMixin(BriefingRoomDrawTableMixin):
    # inherit everything, this class is kept in code for ease of reading
    pass


class BriefingRoomDrawByTeamTableMixin(BriefingRoomDrawTableMixin):

    sort_key = '' # Leave with default sort order

    def populate_table(self, debates, table):
        # unicodedata.normalize gets accented characters (e.g. "Éothéod") to sort correctly
        draw_by_team = [(debate, debate.get_team(side)) for debate, side in product(debates, self.tournament.sides)]
        draw_by_team.sort(key=lambda x: unicodedata.normalize('NFKD', table._team_short_name(x[1])))

        if len(draw_by_team) == 0:
            debates, teams = [], []  # next line can't unpack if draw_by_team is empty
        else:
            debates, teams = zip(*draw_by_team)
        super().populate_table(debates, table, highlight=teams)


class AdminDrawDisplayForSpecificRoundByVenueView(AdministratorMixin,
        BriefingRoomDrawByVenueTableMixin, BaseDisplayDrawForSpecificRoundTableView):
    pass


class AdminDrawDisplayForSpecificRoundByTeamView(AdministratorMixin,
        BriefingRoomDrawByTeamTableMixin, BaseDisplayDrawForSpecificRoundTableView):
    pass


class AdminDrawDisplayForCurrentRoundsByVenueView(AdministratorMixin,
        BriefingRoomDrawByVenueTableMixin, BaseDisplayDrawForCurrentRoundsTableView):
    pass


class AdminDrawDisplayForCurrentRoundsByTeamView(AdministratorMixin,
        BriefingRoomDrawByTeamTableMixin, BaseDisplayDrawForCurrentRoundsTableView):
    pass


class AssistantDrawDisplayForSpecificRoundByVenueView(OptionalAssistantTournamentPageMixin,
        BriefingRoomDrawByVenueTableMixin, BaseDisplayDrawForSpecificRoundTableView):
    assistant_page_permissions = ['all_areas', 'results_draw']

    def is_page_enabled(self, tournament):
        return self.round.is_current and super().is_page_enabled(tournament)


class AssistantDrawDisplayForSpecificRoundByTeamView(OptionalAssistantTournamentPageMixin,
        BriefingRoomDrawByTeamTableMixin, BaseDisplayDrawForSpecificRoundTableView):
    assistant_page_permissions = ['all_areas', 'results_draw']

    def is_page_enabled(self, tournament):
        return self.round.is_current and super().is_page_enabled(tournament)


class AssistantDrawDisplayForCurrentRoundsByVenueView(OptionalAssistantTournamentPageMixin,
        BriefingRoomDrawByVenueTableMixin, BaseDisplayDrawForCurrentRoundsTableView):
    assistant_page_permissions = ['all_areas', 'results_draw']


class AssistantDrawDisplayForCurrentRoundsByTeamView(OptionalAssistantTournamentPageMixin,
        BriefingRoomDrawByTeamTableMixin, BaseDisplayDrawForCurrentRoundsTableView):
    assistant_page_permissions = ['all_areas', 'results_draw']


# ==============================================================================
# Draw Alerts Utilities (Admin)
# ==============================================================================

class AdminDrawUtiltiesMixin:
    """Shared between the admin draw and admin display pages."""

    def get_draw(self):
        if not hasattr(self, '_draw'):
            self._draw = self.round.debate_set_with_prefetches(ordering=('room_rank',),
                    institutions=True, venues=True)
        return self._draw

    @cached_property
    def adjudicator_conflicts(self):
        return adjudicator_conflicts_display(self.get_draw())

    @cached_property
    def venue_conflicts(self):
        return venue_conflicts_display(self.get_draw())

    def get_context_data(self, **kwargs):
        # Need to call super() first, so that get_table() can populate
        # self.venue_conflicts and self.adjudicator_conflicts.
        data = super().get_context_data(**kwargs)

        def _count(conflicts):
            return [len([x for x in c if x[0] != 'success']) > 0 for c in conflicts.values()].count(True)

        data['debates_with_adj_conflicts'] = _count(self.adjudicator_conflicts)
        data['debates_with_venue_conflicts'] = _count(self.venue_conflicts)
        data['active_adjs'] = self.round.active_adjudicators.count()
        data['debates_in_round'] = self.round.debate_set.count()
        data['preformed_panels_in_round'] = self.round.preformedpanel_set.count()
        if hasattr(self, 'highlighted_cells_exist'):
            data['highlighted_cells_exist'] = self.highlighted_cells_exist
        return data


# ==============================================================================
# Draw Display Index (Admin)
# ==============================================================================

class BaseDrawDisplayIndexView(AdminDrawUtiltiesMixin, RoundMixin, TemplateView):
    pass


class AdminDrawDisplayView(AdministratorMixin, BaseDrawDisplayIndexView):
    template_name = 'draw_display_admin.html'


class AssistantDrawDisplayView(CurrentRoundMixin, OptionalAssistantTournamentPageMixin, BaseDrawDisplayIndexView):
    template_name = 'draw_display_assistant.html'
    assistant_page_permissions = ['all_areas', 'results_draw']


class EmailAdjudicatorAssignmentsView(RoundTemplateEmailCreateView):
    page_subtitle = _("Adjudicator Assignments")

    event = BulkNotification.EVENT_TYPE_ADJ_DRAW
    subject_template = 'adj_email_subject'
    message_template = 'adj_email_message'

    round_redirect_pattern_name = 'draw-display'

    dadj_type_display = dict(DebateAdjudicator.TYPE_CHOICES)

    def get_extra(self):
        extra = super().get_extra()
        extra['url'] = self.request.build_absolute_uri(
            reverse_tournament('privateurls-person-index', self.tournament, kwargs={'url_key': '0'}))[:-2]
        return extra

    def get_person_type(self, person, **kwargs):
        return person.position

    def get_table(self):
        table = super().get_table()

        table.add_column({'key': 'pos', 'title': _("Position")}, [{
            'text': self.dadj_type_display[p.position],
        } for p in self.get_queryset()])

        return table

    def get_queryset(self):
        return Adjudicator.objects.filter(debateadjudicator__debate__round=self.round).annotate(
            position=Subquery(DebateAdjudicator.objects.filter(adjudicator_id=OuterRef('pk'), debate__round=self.round).values('type')[:1]),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'id': pos, 'name': d} for pos, d in DebateAdjudicator.TYPE_CHOICES
        ]
        return context


class EmailTeamAssignmentsView(RoundTemplateEmailCreateView):
    page_subtitle = _("Team Pairings")

    event = BulkNotification.EVENT_TYPE_TEAM_DRAW
    subject_template = 'team_draw_email_subject'
    message_template = 'team_draw_email_message'

    round_redirect_pattern_name = 'draw-display'

    def get_queryset(self):
        return Speaker.objects.filter(team__in=self.round.active_teams)


# ==============================================================================
# Draw Creation (Admin)
# ==============================================================================

class AdminDrawView(RoundMixin, AdministratorMixin, AdminDrawUtiltiesMixin, VueTableTemplateView):
    detailed = False

    def get_page_title(self):
        round = self.round
        self.page_emoji = '👀'
        if round.draw_status == Round.STATUS_NONE:
            title = _("No Draw")
        elif round.draw_status == Round.STATUS_DRAFT:
            title = _("Draft Draw")
        elif round.draw_status in [Round.STATUS_CONFIRMED, Round.STATUS_RELEASED]:
            self.page_emoji = '👏'
            title = _("Draw")
        else:
            logger.error("Unrecognised draw status: %s", round.draw_status)
            title = _("Draw")
        return title % {'round': round.name}

    def get_bp_position_balance_table(self):
        draw = self.get_draw()
        teams = Team.objects.filter(debateteam__debate__round=self.round)
        side_histories_before = get_side_history(teams, self.tournament.sides, self.round.prev.seq)
        side_histories_now = get_side_history(teams, self.tournament.sides, self.round.seq)
        metrics = self.tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics[0:1], ())
        standings = generator.generate(teams, round=self.round.prev)
        draw_table = PositionBalanceReportDrawTableBuilder(view=self)
        draw_table.build(draw, teams, side_histories_before, side_histories_now, standings)
        self.highlighted_cells_exist = any(draw_table.get_imbalance_category(team) is not None for team in teams)
        return draw_table

    def get_standard_table(self):
        r = self.round

        if r.is_break_round:
            sort_key = "room-rank"
            sort_order = 'asc'
        else:
            sort_key = "bracket"
            sort_order = 'desc'

        table = AdminDrawTableBuilder(view=self, sort_key=sort_key,
                                      sort_order=sort_order,
                                      empty_title=_("No debates in this round"))

        draw = self.get_draw()
        populate_history(draw)

        if r.is_break_round:
            table.add_room_rank_columns(draw)
        else:
            table.add_debate_bracket_columns(draw)

        table.add_debate_venue_columns(draw, for_admin=True)
        table.add_debate_team_columns(draw)

        # For draw details and draw draft pages
        if (r.draw_status == Round.STATUS_DRAFT or self.detailed) and r.prev:
            teams = Team.objects.filter(debateteam__debate__round=r)
            metrics = self.tournament.pref('team_standings_precedence')

            if self.tournament.pref('teams_in_debate') == 'two':
                pullup_metric = PowerPairedDrawGenerator.PULLUP_RESTRICTION_METRICS[self.tournament.pref('draw_pullup_restriction')]
            else:
                pullup_metric = None

            # subrank only makes sense if there's a second metric to rank on
            rankings = ('rank', 'subrank') if len(metrics) > 1 else ('rank',)
            generator = TeamStandingsGenerator(metrics, rankings,
                extra_metrics=(pullup_metric,) if pullup_metric and pullup_metric not in metrics else ())
            standings = generator.generate(teams, round=r.prev)
            if not r.is_break_round:
                table.add_debate_ranking_columns(draw, standings)
            else:
                self._add_break_rank_columns(table, draw, r.break_category)
            table.add_debate_metric_columns(draw, standings)
            table.add_debate_side_history_columns(draw, r.prev)
        elif not (r.draw_status == Round.STATUS_DRAFT or self.detailed):
            table.add_debate_adjudicators_column(draw, show_splits=False, for_admin=True)

        table.add_draw_conflicts_columns(draw, self.venue_conflicts, self.adjudicator_conflicts)

        if not r.is_break_round:
            table.highlight_rows_by_column_value(column=0) # highlight first row of a new bracket

        return table

    def get_table(self):
        r = self.round
        if r.draw_status == Round.STATUS_NONE:
            return TabbycatTableBuilder(view=self)  # blank
        elif self.tournament.pref('teams_in_debate') == 'bp' and \
                r.draw_status == Round.STATUS_DRAFT and r.prev is not None and \
                not r.is_break_round:
            return self.get_bp_position_balance_table()
        else:
            return self.get_standard_table()

    def _add_break_rank_columns(self, table, draw, category):
        for side in self.tournament.sides:
            # Translators: e.g. "Affirmative: Break rank"
            tooltip = _("%(side)s: Break rank") % {
                'side': get_side_name(self.tournament, side, 'full'),
            }
            tooltip = tooltip.capitalize()
            # Translators: "BR" stands for "Break rank"
            key = format_html("{}<br>{}", get_side_name(self.tournament, side, 'abbr'), _("BR"))

            table.add_column(
                {'tooltip': tooltip, 'key': key, 'text': key},
                [d.get_team(side).break_rank_for_category(category) for d in draw],
            )

    def get_template_names(self):
        if self.round.draw_status == Round.STATUS_NONE:
            return ["draw_status_none.html"]
        elif self.round.draw_status == Round.STATUS_DRAFT:
            return ["draw_status_draft.html"]
        elif self.round.draw_status in [Round.STATUS_CONFIRMED, Round.STATUS_RELEASED]:
            return ["draw_status_confirmed.html"]
        else:
            logger.error("Unrecognised draw status: %s", self.round.draw_status)
            return ["base.html"]


class AdminDrawWithDetailsView(AdminDrawView):
    detailed = True
    page_emoji = '👀'
    use_template_subtitle = False  # Use the "for Round n" subtitle

    def get_page_title(self):
        return _("Draw with Details")

    def get_template_names(self):
        return ["draw_subpage.html"]


class PositionBalanceReportView(RoundMixin, AdministratorMixin, VueTableTemplateView):
    page_emoji = "⚖"
    page_title = _("Position Balance Report")
    tables_orientation = 'rows'

    def get_context_data(self, **kwargs):
        kwargs['cost_func'] = self.get_position_cost_function_str()
        return super().get_context_data(**kwargs)

    def get_position_cost_function_str(self):
        cost_func = self.tournament.pref('bp_position_cost')
        if cost_func == 'entropy':
            renyi_order = self.tournament.pref('bp_renyi_order')
            cost_func_str = _("Rényi entropy of order %(order)s" % {'order': renyi_order})
            if renyi_order == 1:
                # Translators: This is appended to the string "Rényi entropy of order 1.0"
                cost_func_str += _(" (<i>i.e.</i>, Shannon entropy)")
            return mark_safe(cost_func_str)
        else:
            for k, v in BPPositionCost.choices:
                if k == cost_func:
                    return v
            else:
                logger.error("Unknown position cost function option: %s", cost_func)
                return "Unknown"  # don't translate, should never happen

    def get_tables(self):
        if self.tournament.pref('teams_in_debate') != 'bp':
            logger.warning("Tried to access position balance report for a non-BP tournament")
            return []
        if self.round.prev is None:
            logger.warning("Tried to access position balance report for first round")
            return []
        if self.round.is_break_round:
            logger.warning("Tried to access position balance report for a break round")
            return []

        draw = self.round.debate_set_with_prefetches(ordering=('room_rank',), institutions=True)
        teams = Team.objects.filter(debateteam__debate__round=self.round)
        side_histories_before = get_side_history(teams, self.tournament.sides, self.round.prev.seq)
        side_histories_now = get_side_history(teams, self.tournament.sides, self.round.seq)
        metrics = self.tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics[0:1], ())
        standings = generator.generate(teams, round=self.round.prev)

        summary_table = PositionBalanceReportSummaryTableBuilder(view=self,
                title=_("Teams with position imbalances"),
                empty_title=_("No teams with position imbalances! Hooray!") + " 😊")
        summary_table.build(draw, teams, side_histories_before, side_histories_now, standings)

        draw_table = PositionBalanceReportDrawTableBuilder(view=self, title=_("Annotated draw"))
        draw_table.build(draw, teams, side_histories_before, side_histories_now, standings)

        return [summary_table, draw_table]

    def get_template_names(self):
        # Show an error page if this isn't a BP tournament or if it's the first round
        if self.tournament.pref('teams_in_debate') != 'bp':
            return ['position_balance_nonbp.html']
        elif self.round.prev is None:
            return ['position_balance_round1.html']
        elif self.round.is_break_round:
            return ['position_balance_break.html']
        else:
            return ['position_balance.html']


# ==============================================================================
# Draw Status POSTS
# ==============================================================================

class DrawStatusEdit(LogActionMixin, AdministratorMixin, RoundMixin, PostOnlyRedirectView):
    round_redirect_pattern_name = 'draw'


class CreateDrawView(DrawStatusEdit):

    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_CREATE

    def post(self, request, *args, **kwargs):
        if self.round.draw_status != Round.STATUS_NONE:
            messages.error(request, _("Could not create draw for %(round)s, there was already a draw!") % {'round': self.round.name})
            return super().post(request, *args, **kwargs)

        try:
            manager = DrawManager(self.round)
            manager.create()
        except DrawUserError as e:
            messages.error(request, mark_safe(_(
                "<p>The draw could not be created, for the following reason: "
                "<em>%(message)s</em></p>\n"
                "<p>Please fix this issue before attempting to create the draw.</p>",
            ) % {'message': str(e)}))
            logger.warning("User error creating draw: " + str(e), exc_info=True)
            return HttpResponseRedirect(reverse_round('availability-index', self.round))
        except DrawFatalError as e:
            messages.error(request, mark_safe(_(
                "<p>The draw could not be created, because the following error occurred: "
                "<em>%(message)s</em></p>\n"
                "<p>If this issue persists and you're not sure how to resolve it, please "
                "contact the developers.</p>",
            ) % {'message': str(e)}))
            logger.exception("Fatal error creating draw: " + str(e))
            return HttpResponseRedirect(reverse_round('availability-index', self.round))
        except StandingsError as e:
            message = _(
                "<p>The team standings could not be generated, because the following error occurred: "
                "<em>%(message)s</em></p>\n"
                "<p>Because generating the draw uses the current team standings, this "
                "prevents the draw from being generated.</p>",
            ) % {'message': str(e)}
            standings_options_url = reverse_tournament('options-tournament-section', self.tournament, kwargs={'section': 'standings'})
            instructions = BaseStandingsView.admin_standings_error_instructions % {'standings_options_url': standings_options_url}
            messages.error(request, mark_safe(message + instructions))
            logger.exception("Error generating standings for draw: " + str(e))
            return HttpResponseRedirect(reverse_round('availability-index', self.round))

        relevant_adj_venue_constraints = VenueConstraint.objects.filter(
                adjudicator__in=self.tournament.relevant_adjudicators)
        if not relevant_adj_venue_constraints.exists():
            allocate_venues(self.round)
        else:
            messages.warning(request, _("Rooms were not auto-allocated because there are one or more adjudicator room constraints. "
                "You should run room allocations after allocating adjudicators."))

        self.log_action()
        return super().post(request, *args, **kwargs)


class ConfirmDrawCreationView(DrawStatusEdit):
    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_CONFIRM

    def post(self, request, *args, **kwargs):
        if self.round.draw_status != Round.STATUS_DRAFT:
            return HttpResponseBadRequest("Draw status is not DRAFT")

        self.round.draw_status = Round.STATUS_CONFIRMED
        self.round.save()
        self.log_action()
        return super().post(request, *args, **kwargs)


class DrawRegenerateView(DrawStatusEdit):
    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_REGENERATE
    round_redirect_pattern_name = 'availability-index'

    def post(self, request, *args, **kwargs):
        delete_round_draw(self.round)
        self.log_action()
        messages.success(request, _("Deleted the draw. You can now recreate it as normal."))
        return super().post(request, *args, **kwargs)


class ConfirmDrawRegenerationView(AdministratorMixin, TemplateView):
    template_name = "draw_confirm_regeneration.html"


class DrawReleaseView(DrawStatusEdit):
    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_RELEASE
    round_redirect_pattern_name = 'draw-display'

    def post(self, request, *args, **kwargs):
        if self.round.draw_status != Round.STATUS_CONFIRMED:
            return HttpResponseBadRequest("Draw status is not CONFIRMED")

        self.round.draw_status = Round.STATUS_RELEASED
        self.round.save()
        self.log_action()

        messages.success(request, _("Released the draw."))
        return super().post(request, *args, **kwargs)


class DrawUnreleaseView(DrawStatusEdit):
    action_log_type = ActionLogEntry.ACTION_TYPE_DRAW_UNRELEASE
    round_redirect_pattern_name = 'draw-display'

    def post(self, request, *args, **kwargs):
        if self.round.draw_status != Round.STATUS_RELEASED:
            return HttpResponseBadRequest("Draw status is not released")

        self.round.draw_status = Round.STATUS_CONFIRMED
        self.round.save()
        self.log_action()
        messages.success(request, _("Unreleased the draw."))
        return super().post(request, *args, **kwargs)


class SetRoundStartTimeView(DrawStatusEdit):
    action_log_type = ActionLogEntry.ACTION_TYPE_ROUND_START_TIME_SET
    round_redirect_pattern_name = 'draw-display'

    def post(self, request, *args, **kwargs):
        time_text = request.POST["start_time"]
        try:
            time = datetime.datetime.strptime(time_text, "%H:%M").time()
        except ValueError:
            messages.error(request, _("Sorry, \"%(input)s\" isn't a valid time. It must "
                           "be in 24-hour format, with a colon, for "
                           "example: \"13:57\".") % {'input': time_text})
            return super().post(request, *args, **kwargs)

        self.round.starts_at = time
        self.round.save()

        self.log_action()

        return super().post(request, *args, **kwargs)


# ==============================================================================
# Sides Editing and Viewing
# ==============================================================================

class BaseSideAllocationsView(TournamentMixin, VueTableTemplateView):

    page_title = gettext_lazy("Side Pre-Allocations")

    def get_table(self):
        teams = self.tournament.team_set.all()
        rounds = self.tournament.prelim_rounds()

        tsas = dict()
        for tsa in TeamSideAllocation.objects.filter(round__in=rounds):
            try:
                tsas[(tsa.team.id, tsa.round.seq)] = get_side_name(self.tournament, tsa.side, 'abbr')
            except ValueError:
                pass

        table = TabbycatTableBuilder(view=self)
        table.add_team_columns(teams)

        headers = [round.abbreviation for round in rounds]
        data = [[tsas.get((team.id, round.seq), "—") for round in rounds] for team in teams]
        table.add_columns(headers, data)

        return table


class SideAllocationsView(AdministratorMixin, BaseSideAllocationsView):
    pass


class PublicSideAllocationsView(PublicTournamentPageMixin, BaseSideAllocationsView):
    public_page_preference = 'public_side_allocations'


class EditDebateTeamsView(DebateDragAndDropMixin, AdministratorMixin, TemplateView):
    template_name = "edit_debate_teams.html"
    page_title = gettext_lazy("Edit Matchups")
    prefetch_teams = False # Fetched in full as get_serialised

    def get_serialised_allocatable_items(self):
        # TODO: account for shared teams
        teams = Team.objects.filter(tournament=self.tournament).prefetch_related('speaker_set')
        teams = annotate_availability(teams, self.round)
        populate_win_counts(teams)
        serialized_teams = EditDebateTeamsTeamSerializer(teams, many=True)
        return self.json_render(serialized_teams.data)

    def debates_or_panels_factory(self, debates):
        return EditDebateTeamsDebateSerializer(
            debates, many=True, context={'sides': self.tournament.sides})
