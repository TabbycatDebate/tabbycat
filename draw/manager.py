from tournament.models import Round
from standings.teams import TeamStandingsGenerator

from .models import Debate, TeamPositionAllocation
from .generator import DrawGenerator

OPTIONS_TO_CONFIG_MAPPING = {
    "avoid_institution": "draw_rules__avoid_same_institution",
    "avoid_history": "draw_rules__avoid_team_history",
    "history_penalty": "draw_rules__team_history_penalty",
    "institution_penalty": "draw_rules__team_institution_penalty",
    "side_allocations": "draw_rules__draw_side_allocations",
    "avoid_conflicts": "draw_rules__draw_avoid_conflicts",
    "odd_bracket"     : "draw_rules__draw_odd_bracket",
    "pairing_method"  : "draw_rules__draw_pairing_method",
}

TPA_MAP = {TeamPositionAllocation.POSITION_AFFIRMATIVE: "aff",
           TeamPositionAllocation.POSITION_NEGATIVE: "neg"}

def DrawManager(round, active_only=True):
    if round.draw_type == Round.DRAW_RANDOM:


class BaseDrawManager:
    """Creates, modifies and retrieves relevant Debate objects relating to a draw."""

    relevant_options = ["avoid_institution", "avoid_history", "history_penalty", "institution_penalty", "side_allocations"]

    def __init__(self, round, active_only=True):
        self.round = round
        self.debate_set = round.debate_set
        self.active_only = active_only

    def get_teams(self):
        return self.round.active_teams.all() if self.active_only else self.round.tournament.team_set.all()

    def _populate_aff_counts(self, teams):
        if self.round.prev:
            prev_seq = self.round.prev.seq
            for team in teams:
                team.aff_count = team.get_aff_count(prev_seq)
        else:
            for team in teams:
                team.aff_count = 0

    def _populate_team_position_allocations(self, teams):
        tpas = dict()
        for tpa in self.round.teampositionallocation_set.all():
            tpas[tpa.team] = TPA_MAP[tpa.position]
        for team in teams:
            if team in tpas:
                team.allocated_side = tpas[team]

    def _assign_venues(self, pairings):
        venues = list(self.active_venues.order_by('-priority')[:len(pairings)])
        if len(venues) < len(pairings):
            raise RuntimeError("There are %d debates but only %d venues." % (len(pairings), len(venues)))

        random.shuffle(venues)
        random.shuffle(pairings)  # to avoid IDs indicating room ranks

        # CONTINUE HERE - assign venues by division

    def _make_debates(self, pairings):

        for pairing in pairings:
            try:
                if pairing.division:
                    if (pairing.teams[0].type == Team.TYPE_BYE) or (pairing.teams[1].type == Team.TYPE_BYE):
                        selected_venue = None
                    else:
                        selected_venue = next(v for v in venues
                                if v.group == pairing.division.venue_group)
                        venues.pop(venues.index(selected_venue))
                else:
                    selected_venue = venues.pop(0)
            except:
                print("Error assigning venues")
                selected_venue = None

            debate = Debate(round=self, venue=selected_venue)
            debate.division = pairing.division
            debate.bracket = pairing.bracket
            debate.room_rank = pairing.room_rank
            debate.flags = ",".join(pairing.flags)  # comma-separated list
            debate.save()

            DebateTeam(debate=debate, team=pairing.teams[0], position=DebateTeam.POSITION_AFFIRMATIVE).save()
            DebateTeam(debate=debate, team=pairing.teams[1], position=DebateTeam.POSITION_NEGATIVE).save()

    def delete(self):
        self.debate_set.all().delete()

    def create(self):
        """Generates a draw and populates the database with it."""

        if self.round.draw_status == Round.STATUS_NONE:
            raise RuntimeError("Tried to create a draw on round that already has a draw")

        self.delete()

        teams = self.get_teams()
        self._populate_aff_counts(teams)
        self._populate_team_position_allocations(teams)

        options = dict()
        for key in self.relevant_options:
            options[key] = self.round.tournament.preferences[OPTIONS_TO_CONFIG_MAPPING[key]]
        if options["side_allocations"] == "manual-ballot":
            options["side_allocations"] = "balance"

        drawer = DrawGenerator(self.draw_type, teams, self.round, results=None, **options)
        pairings = drawer.generate()
        self._make_debates(pairings)
        self.round.draw_status = self.STATUS_DRAFT
        self.round.save()


class RandomDrawManager(BaseDrawManager):
    draw_type = "random"
    relevant_options = BaseDrawManager.relevant_options + ["avoid_conflicts"]


class ManualDrawManager(BaseDrawManager):
    draw_type = "manual"


class PowerPairedDrawManager(BaseDrawManager):
    draw_type = "power_paired"
    relevant_options = BaseDrawManager.relevant_options + ["avoid_conflicts", "odd_bracket", "pairing_method"]

    def get_teams(self):
        metrics = self.round.tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'), tiebreak="random")
        standings = generator.generate(super().get_teams(), round=self.round.prev)

        ranked = []
        for standing in standings:
            team = standings.team
            team.points = next(standing.itermetrics())
            ranked.append(team)

        return ranked


class RoundRobinDrawManager(BaseDrawManager):
    draw_type = "round_robin"
