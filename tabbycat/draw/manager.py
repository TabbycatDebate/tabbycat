import random

from django.utils.translation import ugettext as _

from participants.utils import get_side_counts
from tournaments.models import Round
from standings.teams import TeamStandingsGenerator

from .models import Debate, DebateTeam
from .generator import DrawGenerator, DrawUserError, Pairing

OPTIONS_TO_CONFIG_MAPPING = {
    "avoid_institution"     : "draw_rules__avoid_same_institution",
    "avoid_history"         : "draw_rules__avoid_team_history",
    "history_penalty"       : "draw_rules__team_history_penalty",
    "institution_penalty"   : "draw_rules__team_institution_penalty",
    "side_allocations"      : "draw_rules__draw_side_allocations",
    "avoid_conflicts"       : "draw_rules__draw_avoid_conflicts",
    "odd_bracket"           : "draw_rules__draw_odd_bracket",
    "pairing_method"        : "draw_rules__draw_pairing_method",
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
    return klass(round, active_only)


class BaseDrawManager:
    """Creates, modifies and retrieves relevant Debate objects relating to a draw."""

    def __init__(self, round, active_only=True):
        self.round = round
        self.teams_in_debate = self.round.tournament.pref('teams_in_debate')
        self.active_only = active_only

    def get_relevant_options(self):
        if self.teams_in_debate == 'two':
            return ["avoid_institution", "avoid_history", "history_penalty", "institution_penalty"]
        else:
            return []

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

    def _populate_side_counts(self, teams):
        sides = self.round.tournament.sides

        if self.round.prev:
            prev_seq = self.round.prev.seq
            side_counts = get_side_counts(teams, sides, prev_seq)
            for team in teams:
                team.side_counts = side_counts[team.id]
        else:
            for team in teams:
                team.side_counts = [0] * len(sides)

    def _populate_team_side_allocations(self, teams):
        tsas = dict()
        for tsa in self.round.teamsideallocation_set.all():
            tsas[tsa.team] = tsa.side
        for team in teams:
            if team in tsas:
                team.allocated_side = tsas[team]

    def _make_debates(self, pairings):
        random.shuffle(pairings)  # to avoid IDs indicating room ranks

        for pairing in pairings:
            debate = Debate(round=self.round)
            debate.division = pairing.division
            debate.bracket = pairing.bracket
            debate.room_rank = pairing.room_rank
            debate.flags = ",".join(pairing.flags)  # comma-separated list
            debate.save()

            for team, side in zip(pairing.teams, self.round.tournament.sides):
                DebateTeam.objects.create(debate=debate, team=team, side=side,
                        flags=",".join(pairing.get_team_flags(team)))

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

        self._populate_side_counts(teams)
        if options.get("side_allocatons") == "preallocated":
            self._populate_team_side_allocations(teams)

        drawer = DrawGenerator(self.teams_in_debate, self.draw_type, teams,
                results=results, rrseq=rrseq, **options)
        pairings = drawer.generate()
        self._make_debates(pairings)
        self.round.draw_status = Round.STATUS_DRAFT
        self.round.save()


class RandomDrawManager(BaseDrawManager):
    draw_type = "random"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 'two':
            options.extend(["avoid_conflicts", "side_allocations"])
        return options


class ManualDrawManager(BaseDrawManager):
    draw_type = "manual"


class PowerPairedDrawManager(BaseDrawManager):
    draw_type = "power_paired"

    def get_relevant_options(self):
        options = super().get_relevant_options()
        if self.teams_in_debate == 'two':
            options.extend(["avoid_conflicts", "odd_bracket", "pairing_method", "side_allocations"])
        elif self.teams_in_debate == 'bp':
            options.extend(["pullup", "position_cost", "assignment_method", "renyi_order", "exponent"])
        return options

    def get_teams(self):
        """Get teams in ranked order."""
        metrics = self.round.tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'), tiebreak="random")
        standings = generator.generate(super().get_teams(), round=self.round.prev)

        ranked = []
        for standing in standings:
            team = standing.team
            team.points = next(standing.itermetrics())
            ranked.append(team)

        return ranked


class RoundRobinDrawManager(BaseDrawManager):
    draw_type = "round_robin"

    def get_rrseq(self):
        prior_rrs = list(self.round.tournament.round_set.filter(draw_type=Round.DRAW_ROUNDROBIN).order_by('seq'))
        try:
            rr_seq = prior_rrs.index(self.round) + 1 # Dont 0-index
        except ValueError:
            raise RuntimeError("Tried to calculate an effective round robin seq but couldn't")

        return rr_seq


class BaseEliminationDrawManager(BaseDrawManager):
    def get_teams(self):
        breaking_teams = self.round.break_category.breakingteam_set_competing.order_by(
                'break_rank').select_related('team')
        return [bt.team for bt in breaking_teams]


class FirstEliminationDrawManager(BaseEliminationDrawManager):
    draw_type = "first_elimination"


class EliminationDrawManager(BaseEliminationDrawManager):
    draw_type = "elimination"

    def get_results(self):
        last_round = self.round.break_category.round_set.filter(seq__lt=self.round.seq).order_by('-seq').first()
        debates = last_round.debate_set.all()
        result = [Pairing.from_debate(debate) for debate in debates]
        return result


DRAW_MANAGER_CLASSES = {
    ('two', Round.DRAW_RANDOM): RandomDrawManager,
    ('two', Round.DRAW_POWERPAIRED): PowerPairedDrawManager,
    ('two', Round.DRAW_ROUNDROBIN): RoundRobinDrawManager,
    ('two', Round.DRAW_MANUAL): ManualDrawManager,
    ('two', Round.DRAW_FIRSTBREAK): FirstEliminationDrawManager,
    ('two', Round.DRAW_BREAK): EliminationDrawManager,
    ('bp', Round.DRAW_RANDOM): RandomDrawManager,
    ('bp', Round.DRAW_MANUAL): ManualDrawManager,
    ('bp', Round.DRAW_POWERPAIRED): PowerPairedDrawManager,
}
