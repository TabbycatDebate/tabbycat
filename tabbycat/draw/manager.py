import logging
import random
from operator import add
from typing import List, Tuple, TYPE_CHECKING

from django.utils.translation import gettext as _

from draw.generator.powerpair import BasePowerPairedDrawGenerator
from participants.utils import get_side_history
from results.models import BallotSubmission, TeamScore
from standings.teams import TeamStandingsGenerator
from tournaments.models import Round

from .generator import BPEliminationResultPairing, DrawGenerator, DrawUserError, ResultPairing
from .generator.utils import ispow2
from .models import Debate, DebateTeam
from .types import DebateSide

if TYPE_CHECKING:
    from participants.models import Team
    from .generator.pairing import BasePairing

logger = logging.getLogger(__name__)

OPTIONS_TO_CONFIG_MAPPING = {
    "avoid_institution"     : "draw_rules__avoid_same_institution",
    "avoid_history"         : "draw_rules__avoid_team_history",
    "history_penalty"       : "draw_rules__team_history_penalty",
    "institution_penalty"   : "draw_rules__team_institution_penalty",
    "pullup_debates_penalty": "draw_rules__pullup_debates_penalty",
    "side_penalty"          : "draw_rules__side_penalty",
    "pairing_penalty"       : "draw_rules__pairing_penalty",
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


def DrawManager(round: Round, active_only: bool = True, draw_type: Round.DrawType | str | None = None):  # noqa: N802 (factory function)
    teams_in_debate = round.tournament.pref('teams_in_debate')
    draw_type = draw_type or round.draw_type
    try:
        if teams_in_debate in [2, 4]:
            klass = DRAW_MANAGER_CLASSES[(teams_in_debate, round.draw_type)]
        else:
            klass = DRAW_MANAGER_CLASSES[(None, round.draw_type)]
    except KeyError:
        if teams_in_debate == 2:
            raise DrawUserError(_("The draw type %(type)s can't be used with two-team formats.") % {'type': round.get_draw_type_display()})
        elif teams_in_debate == 4:
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
        if self.teams_in_debate == 2:
            return [
                "avoid_institution",
                "avoid_history",
                "history_penalty",
                "institution_penalty",
                "pullup_debates_penalty",
                "side_penalty",
                "pairing_penalty",
                "avoid_conflicts",
            ]
        return []

    def n_byes(self, n_teams):
        if self.round.tournament.pref('bye_team_selection') != 'off':
            return n_teams % len(self.round.tournament.sides)
        return 0

    def get_generator_type(self):
        return self.generator_type

    def get_teams(self) -> Tuple[List['Team'], List['Team']]:
        if self.active_only:
            teams = self.round.active_teams.all()
        else:
            teams = self.round.tournament.team_set.all()

        teams = list(teams)
        n_byes = self.n_byes(len(teams))
        if n_byes:
            return teams[:-n_byes], teams[-n_byes:]
        return teams, []

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

    def _make_debates(self, pairings: List['BasePairing']) -> list[Debate]:
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
        return list(debates.values())

    def _make_bye_debates(self, byes: List['Team'], room_rank: int) -> list[Debate]:
        """We'd want the room rank as to always show byes at the bottom"""
        debates = []
        for i, bye in enumerate(byes, start=room_rank + 1):
            debate = Debate(round=self.round, bracket=-1, room_rank=i)
            debate.save()
            debates.append(debate)

            dt = DebateTeam(debate=debate, team=bye, side=DebateSide.BYE)
            dt.save()

            if self.round.tournament.pref('bye_team_results') == 'points':
                bs = BallotSubmission(submitter_type=BallotSubmission.Submitter.AUTOMATION, confirmed=True, debate=debate)
                bs.save()
                TeamScore.objects.create(ballot_submission=bs, debate_team=dt, points=1, win=True)
        return debates

    def delete(self):
        self.round.debate_set.all().delete()

    def create(self, options: dict | None = None) -> list[Debate]:
        """Generates a draw and populates the database with it."""

        if self.round.draw_status != Round.Status.NONE:
            raise RuntimeError("Tried to create a draw on round that already has a draw")

        self.delete()

        if options is None:
            options = dict()
        for key in self.get_relevant_options():
            if key not in options:
                options[key] = self.round.tournament.preferences[OPTIONS_TO_CONFIG_MAPPING[key]]
        if options.get("side_allocations") == "manual-ballot":
            options["side_allocations"] = "balance"

        teams, byes = self.get_teams()
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
        debates = self._make_debates(pairings)

        debates.extend(self._make_bye_debates(byes, max([p.room_rank for p in pairings], default=0)))

        self.round.draw_status = Round.Status.DRAFT
        self.round.save()

        return debates


class RandomDrawManager(BaseDrawManager):
    generator_type = "random"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 2:
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
        if self.teams_in_debate == 2:
            options.extend([
                "avoid_conflicts", "odd_bracket", "pairing_method",
                "pullup_restriction", "side_allocations",
            ])
        elif self.teams_in_debate == 4:
            options.extend(["pullup", "position_cost", "assignment_method", "renyi_order", "exponent"])
        return options

    def get_teams(self) -> Tuple[List['Team'], List['Team']]:
        """Get teams in ranked order."""
        teams = add(*super().get_teams())
        teams = self.round.tournament.team_set.filter(id__in=[t.id for t in teams])

        metrics = self.round.tournament.pref('team_standings_precedence')
        pullup_metric = BasePowerPairedDrawGenerator.PULLUP_RESTRICTION_METRICS[self.round.tournament.pref('draw_pullup_restriction')]
        extra_metrics = {pullup_metric} if pullup_metric is not None else set()

        pullup_debates_penalty = self.round.tournament.pref("pullup_debates_penalty")
        if pullup_debates_penalty > 0:
            extra_metrics.add("pullup_debates")
        extra_metrics -= set(metrics)

        generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'), tiebreak="random", extra_metrics=list(extra_metrics))
        standings = generator.generate(teams, round=self.round.prev)

        ranked = []
        for standing in standings:
            team = standing.team
            team.points = next(standing.itermetrics(), 0) or 0
            team.subrank = standing.get_ranking('subrank')
            if pullup_debates_penalty > 0:
                team.pullup_debates = standing.metrics.get("pullup_debates", 0)
            if pullup_metric:
                setattr(team, pullup_metric, standing.metrics[pullup_metric])
            ranked.append(team)

        n_byes = self.n_byes(len(ranked))
        if n_byes:
            if self.round.tournament.pref('bye_team_selection') == 'random':
                byes = []
                for i in range(n_byes):
                    byes.append(ranked.pop(random.randrange(len(ranked))))
                return ranked, byes
            elif self.round.tournament.pref('bye_team_selection') == 'lowest':
                return ranked[:-n_byes], ranked[-n_byes:]
            else:
                raise RuntimeError("Bye team(s) created without recognized selection option")

        return ranked, []


class SeededDrawManager(BaseDrawManager):
    generator_type = "power_paired"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 2:
            options.extend(["avoid_conflicts", "pairing_method", "side_allocations"])
        elif self.teams_in_debate == 4:
            options.extend(["assignment_method"])
        return options

    def get_teams(self) -> Tuple[List['Team'], List['Team']]:
        """Get teams in seeded order."""
        teams = add(*super().get_teams())
        random.shuffle(teams)
        teams.sort(key=lambda t: -t.seed)

        byes = []
        n_byes = self.n_byes(len(teams))
        if n_byes:
            if self.round.tournament.pref('bye_team_selection') == 'lowest':
                teams, byes = teams[:-n_byes], teams[-n_byes:]
            else:
                for i in range(n_byes):
                    byes.append(teams.pop(random.randrange(len(teams))))

        for team in teams:
            team.points = 0
            team.subrank = team.seed + 1

        return teams, byes


class RoundRobinDrawManager(BaseDrawManager):
    generator_type = "round_robin"

    def get_rrseq(self):
        prior_rrs = list(self.round.tournament.round_set.filter(draw_type=Round.DrawType.ROUNDROBIN).order_by('seq'))
        try:
            rr_seq = prior_rrs.index(self.round) + 1 # Dont 0-index
        except ValueError:
            raise RuntimeError("Tried to calculate an effective round robin seq but couldn't")

        return rr_seq


class BaseEliminationDrawManager(BaseDrawManager):
    result_pairing_class = None

    def get_teams(self) -> Tuple[List['Team'], List['Team']]:
        breaking_teams = self.round.break_category.breakingteam_set_competing.order_by(
                'break_rank').select_related('team')
        return [bt.team for bt in breaking_teams], []

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
    (2, Round.DrawType.RANDOM): RandomDrawManager,
    (2, Round.DrawType.POWERPAIRED): PowerPairedDrawManager,
    (2, Round.DrawType.ROUNDROBIN): RoundRobinDrawManager,
    (2, Round.DrawType.MANUAL): ManualDrawManager,
    (2, Round.DrawType.ELIMINATION): EliminationDrawManager,
    (2, Round.DrawType.SEEDED): SeededDrawManager,
    (4, Round.DrawType.RANDOM): RandomDrawManager,
    (4, Round.DrawType.MANUAL): ManualDrawManager,
    (4, Round.DrawType.POWERPAIRED): PowerPairedDrawManager,
    (4, Round.DrawType.ELIMINATION): BPEliminationDrawManager,
    (None, Round.DrawType.RANDOM): RandomDrawManager,
    (None, Round.DrawType.MANUAL): ManualDrawManager,
    (None, Round.DrawType.ELIMINATION): EliminationDrawManager,
}
