import logging
import random

from django.utils.translation import gettext as _

from draw.generator.powerpair import PowerPairedDrawGenerator
from participants.utils import get_side_history
from standings.teams import TeamStandingsGenerator
from tournaments.models import Round

from .generator import BPEliminationResultPairing, DrawGenerator, DrawUserError, ResultPairing
from .generator.utils import ispow2
from .models import Debate, DebateTeam

logger = logging.getLogger(__name__)

OPTIONS_TO_CONFIG_MAPPING = {
    "avoid_institution"     : "draw_rules__avoid_same_institution",
    "avoid_history"         : "draw_rules__avoid_team_history",
    "history_penalty"       : "draw_rules__team_history_penalty",
    "institution_penalty"   : "draw_rules__team_institution_penalty",
    "side_allocations"      : "draw_rules__draw_side_allocations",
    "avoid_conflicts"       : "draw_rules__draw_avoid_conflicts",
    "odd_bracket"           : "draw_rules__draw_odd_bracket",
    "pairing_method"        : "draw_rules__draw_pairing_method",
    "pullup_restriction"    : "draw_rules__draw_pullup_restriction",
    "pullup"                : "draw_rules__bp_pullup_distribution",
    "position_cost"         : "draw_rules__bp_position_cost",
    "assignment_method"     : "draw_rules__bp_assignment_method",
    "renyi_order"           : "draw_rules__bp_renyi_order",
    "exponent"              : "draw_rules__bp_position_cost_exponent",
}


def DrawManager(round, active_only=True):  # noqa: N802 (factory function)
    teams_in_debate = round.tournament.pref('teams_in_debate')
    try:
        klass = DRAW_MANAGER_CLASSES[(teams_in_debate, round.draw_type)]
    except KeyError:
        if teams_in_debate == 'two':
            raise DrawUserError(_("The draw type %(type)s can't be used with two-team formats.") % {'type': round.get_draw_type_display()})
        elif teams_in_debate == 'bp':
            raise DrawUserError(_("The draw type %(type)s can't be used with British Parliamentary.") % {'type': round.get_draw_type_display()})
        else:
            raise DrawUserError(_("Unrecognised \"teams in debate\" option: %(option)s") % {'option': teams_in_debate})
    logger.debug("Using draw manager class: %s", klass.__name__)
    return klass(round, active_only)


class BaseDrawManager:
    """Creates, modifies and retrieves relevant Debate objects relating to a draw."""

    generator_type = None

    def __init__(self, round, active_only=True):
        self.round = round
        self.teams_in_debate = self.round.tournament.pref('teams_in_debate')
        self.active_only = active_only

    def get_relevant_options(self):
        if self.teams_in_debate == 'two':
            return ["avoid_institution", "avoid_history", "history_penalty", "institution_penalty"]
        else:
            return []

    def get_generator_type(self):
        return self.generator_type

    def get_teams(self):
        if self.active_only:
            return self.round.active_teams.all()
        else:
            return self.round.tournament.team_set.all()

    def get_results(self):
        # Only needed for EliminationDrawManager
        return None

    def get_rrseq(self):
        # Only needed for RoundRobinDrawManager
        return None

    def _populate_side_history(self, teams):
        sides = self.round.tournament.sides

        if self.round.prev:
            prev_seq = self.round.prev.seq
            side_history = get_side_history(teams, sides, prev_seq)
            for team in teams:
                team.side_history = side_history[team.id]
        else:
            for team in teams:
                team.side_history = [0] * len(sides)

    def _populate_team_side_allocations(self, teams):
        tsas = dict()
        for tsa in self.round.teamsideallocation_set.all():
            tsas[tsa.team] = tsa.side
        for team in teams:
            if team in tsas:
                team.allocated_side = tsas[team]

    def _make_debates(self, pairings):
        random.shuffle(pairings)  # to avoid IDs indicating room ranks

        debates = {}
        debateteams = []

        for pairing in pairings:
            debate = Debate(round=self.round, bracket=pairing.bracket, room_rank=pairing.room_rank, flags=pairing.flags)
            if (self.round.tournament.pref('draw_side_allocations') == "manual-ballot" or
                    self.round.is_break_round):
                debate.sides_confirmed = False
            debates[pairing] = debate

        Debate.objects.bulk_create(debates.values())
        logger.debug("Created %d debates", len(debates))

        for pairing, debate in debates.items():
            for team, side in zip(pairing.teams, self.round.tournament.sides):
                dt = DebateTeam(debate=debate, team=team, side=side, flags=pairing.get_team_flags(team))
                debateteams.append(dt)

        DebateTeam.objects.bulk_create(debateteams)
        logger.debug("Created %d debate teams", len(debateteams))

    def delete(self):
        self.round.debate_set.all().delete()

    def create(self):
        """Generates a draw and populates the database with it."""

        if self.round.draw_status != Round.STATUS_NONE:
            raise RuntimeError("Tried to create a draw on round that already has a draw")

        self.delete()

        options = dict()
        for key in self.get_relevant_options():
            options[key] = self.round.tournament.preferences[OPTIONS_TO_CONFIG_MAPPING[key]]
        if options.get("side_allocations") == "manual-ballot":
            options["side_allocations"] = "balance"

        teams = self.get_teams()
        results = self.get_results()
        rrseq = self.get_rrseq()

        self._populate_side_history(teams)
        if options.get("side_allocations") == "preallocated":
            self._populate_team_side_allocations(teams)

        generator_type = self.get_generator_type()
        logger.debug("Using generator type: %s", generator_type)
        drawer = DrawGenerator(self.teams_in_debate, generator_type, teams,
                results=results, rrseq=rrseq, **options)
        pairings = drawer.generate()
        self._make_debates(pairings)
        self.round.draw_status = Round.STATUS_DRAFT
        self.round.save()


class RandomDrawManager(BaseDrawManager):
    generator_type = "random"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 'two':
            options.extend(["avoid_conflicts", "side_allocations"])
        return options


class ManualDrawManager(BaseDrawManager):
    generator_type = "manual"

    def get_relevant_options(self):
        return []


class PowerPairedDrawManager(BaseDrawManager):
    generator_type = "power_paired"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 'two':
            options.extend([
                "avoid_conflicts", "odd_bracket", "pairing_method",
                "pullup_restriction", "side_allocations",
            ])
        elif self.teams_in_debate == 'bp':
            options.extend(["pullup", "position_cost", "assignment_method", "renyi_order", "exponent"])
        return options

    def get_teams(self):
        """Get teams in ranked order."""
        teams = super().get_teams()

        metrics = self.round.tournament.pref('team_standings_precedence')
        pullup_metric = PowerPairedDrawGenerator.PULLUP_RESTRICTION_METRICS[self.round.tournament.pref('draw_pullup_restriction')]

        generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'), tiebreak="random",
            extra_metrics=(pullup_metric,) if pullup_metric and pullup_metric not in metrics else ())
        standings = generator.generate(teams, round=self.round.prev)

        ranked = []
        for standing in standings:
            team = standing.team
            team.points = next(standing.itermetrics(), 0)
            if pullup_metric:
                setattr(team, pullup_metric, standing.metrics[pullup_metric])
            ranked.append(team)

        return ranked


class RoundRobinDrawManager(BaseDrawManager):
    generator_type = "round_robin"

    def get_rrseq(self):
        prior_rrs = list(self.round.tournament.round_set.filter(draw_type=Round.DRAW_ROUNDROBIN).order_by('seq'))
        try:
            rr_seq = prior_rrs.index(self.round) + 1 # Dont 0-index
        except ValueError:
            raise RuntimeError("Tried to calculate an effective round robin seq but couldn't")

        return rr_seq


class BaseEliminationDrawManager(BaseDrawManager):
    result_pairing_class = None

    def get_teams(self):
        breaking_teams = self.round.break_category.breakingteam_set_competing.order_by(
                'break_rank').select_related('team')
        return [bt.team for bt in breaking_teams]

    def get_results(self):
        if self.round.prev is not None and self.round.prev.is_break_round:
            debates = self.round.prev.debate_set_with_prefetches(ordering=('room_rank',), results=True,
                    adjudicators=False, speakers=False, venues=False)
            pairings = [self.result_pairing_class.from_debate(debate, tournament=self.round.tournament)
                        for debate in debates]
            return pairings
        else:
            return None


class EliminationDrawManager(BaseEliminationDrawManager):
    result_pairing_class = ResultPairing

    def get_generator_type(self):
        if self.round.prev is not None and self.round.prev.is_break_round:
            return "elimination"
        else:
            return "first_elimination"


class BPEliminationDrawManager(BaseEliminationDrawManager):
    result_pairing_class = BPEliminationResultPairing

    def get_generator_type(self):
        break_size = self.round.break_category.break_size
        if break_size % 6 == 0 and ispow2(break_size // 6):
            nprev_rounds = self.round.break_category.round_set.filter(seq__lt=self.round.seq).count()
            if nprev_rounds == 0:
                return "partial_elimination"
            elif nprev_rounds == 1:
                return "after_partial_elimination"
            else:
                return "elimination"
        elif break_size % 4 == 0 and ispow2(break_size // 4):
            if self.round.prev is not None and self.round.prev.is_break_round:
                return "elimination"
            else:
                return "first_elimination"
        else:
            raise DrawUserError(_("The break size (%(size)d) for this break category was invalid. "
                "It must be either six times or four times a power of two.") % {'size': break_size})


DRAW_MANAGER_CLASSES = {
    ('two', Round.DRAW_RANDOM): RandomDrawManager,
    ('two', Round.DRAW_POWERPAIRED): PowerPairedDrawManager,
    ('two', Round.DRAW_ROUNDROBIN): RoundRobinDrawManager,
    ('two', Round.DRAW_MANUAL): ManualDrawManager,
    ('two', Round.DRAW_ELIMINATION): EliminationDrawManager,
    ('bp', Round.DRAW_RANDOM): RandomDrawManager,
    ('bp', Round.DRAW_MANUAL): ManualDrawManager,
    ('bp', Round.DRAW_POWERPAIRED): PowerPairedDrawManager,
    ('bp', Round.DRAW_ELIMINATION): BPEliminationDrawManager,
}
