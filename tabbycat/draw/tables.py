from itertools import islice, zip_longest

from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from participants.utils import get_side_history
from standings.templatetags.standingsformat import metricformat, rankingformat
from tournaments.utils import get_side_name
from utils.tables import TabbycatTableBuilder

from .generator.bphungarian import BPHungarianDrawGenerator


class BaseDrawTableBuilder(TabbycatTableBuilder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.side_history_separator = " " if self.tournament.pref('teams_in_debate') == 'bp' else " / "

    def highlight_rows_by_column_value(self, column):
        highlighted_rows = [i for i in range(1, len(self.data))
                if self.data[i][column] != self.data[i-1][column]]
        for i in highlighted_rows:
            self.data[i] = [self._convert_cell(cell) for cell in self.data[i]]
            for cell in self.data[i]:
                cell['class'] = cell.get('class', '') + ' highlight-row'

    def _prepend_side_header(self, side, name, abbr, text_only=False):
        # Translators: e.g. "Affirmative: Rank", "Government: Draw strength",
        # "Opening government: Total speaker score", "Closing opposition: Number of firsts"
        tooltip = _("%(side)s: %(metric)s") % {
            'side': get_side_name(self.tournament, side, 'full'),
            'metric': name.capitalize(),
        }
        tooltip = tooltip.capitalize()
        key = format_html("{}<br>{}", get_side_name(self.tournament, side, 'abbr'), abbr)

        # Never use icons in this type of column, because we need to differentiate between sides
        header = {
            'key': key,  # no need to translate
            'tooltip': tooltip,
            'text': abbr if text_only else key,
        }

        return header

    def _side_history_by_team(self, side_histories, teams):
        """Given a list of side histories (returned by get_side_history()),
        returns cells that can be used to show the side history for each team
        in `teams`."""
        # Note that the spaces used in the separator are nonbreaking spaces, not normal spaces
        return [{'text': self.side_history_separator.join(map(str, side_histories[team.id]))}
                for team in teams]


class PublicDrawTableBuilder(BaseDrawTableBuilder):

    def add_debate_team_columns(self, debates, highlight=[]):
        all_sides_confirmed = all(debate.sides_confirmed for debate in debates)  # should already be fetched

        for i, side in enumerate(self.tournament.sides, start=1):
            # For BP team names are often longer than the full position label
            if self.tournament.pref('teams_in_debate') == 'bp':
                side_name = get_side_name(self.tournament, side, 'abbr')
            else:
                side_name = get_side_name(self.tournament, side, 'full')

            team_data = []
            for debate, hl in zip_longest(debates, highlight):
                team = debate.get_team(side)
                subtext = None if (all_sides_confirmed or not debate.sides_confirmed) else side_name
                team_data.append(self._team_cell(team, subtext=subtext, show_emoji=True, highlight=team == hl))

            title = side_name if all_sides_confirmed else _("Team %(num)d") % {'num': i}
            header = {'key': side, 'title': title}
            self.add_column(header, team_data)


class AdminDrawTableBuilder(PublicDrawTableBuilder):
    """This just builds on the public draw table builder, so just extend it."""

    def add_room_rank_columns(self, debates):
        header = {
            'key': "room-rank",
            'icon': 'bar-chart-2',
            'tooltip': _("Room rank of this debate"),
        }
        self.add_column(header, [debate.room_rank for debate in debates])

    def add_debate_bracket_columns(self, debates):
        header = {
            'key': "bracket",
            'icon': 'bar-chart-2',
            'tooltip': _("Bracket of this debate"),
        }

        def _fmt(x):
            if int(x) == x:
                return int(x)
            return x

        self.add_column(header, [_fmt(debate.bracket) for debate in debates])

    def _debate_standings_headers(self, standings, info_method, limit=None):
        info_list = getattr(standings, info_method)()
        headers = []
        for i, info in enumerate(islice(info_list, limit)):
            for side in self.tournament.sides:
                header = self._prepend_side_header(side, info['name'], info['abbr'])
                headers.append(header)
        return headers

    def _add_debate_standing_columns(self, debates, standings, itermethod, infomethod, formattext, formatsort, limit=None):
        standings_by_debate = [standings.get_standings(
                [d.get_team(side) for side in self.tournament.sides]) for d in debates]
        cells = []

        for debate in standings_by_debate:
            row = []
            iterators = [islice(getattr(standing, itermethod)(), limit) for standing in debate]
            for metrics in zip(*iterators):
                for i, metric in enumerate(metrics):
                    cell = {'text': formattext(metric), 'sort': formatsort(metric)}
                    if i == 0:
                        cell['class'] = 'highlight-col'
                    row.append(cell)
            cells.append(row)

        headers = self._debate_standings_headers(standings, infomethod, limit)
        self.add_columns(headers, cells)

    def add_debate_metric_columns(self, debates, standings):
        """Adds metric columns for the teams in the debate, ordered first by
        metric, then by side. For example, in a two-team format with metrics
        (wins, speaker score, who-beat-whom), the column order would be:
            A:Wins, N:Wins, A:Spk, N:Spk, A:WBW, N:WBW
        """
        def formatsort(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return 99999

        # In BP, only list first two metrics, there's not enough space for more
        limit = 2 if self.tournament.pref('teams_in_debate') == 'bp' else None

        return self._add_debate_standing_columns(debates, standings, 'itermetrics',
                'metrics_info', metricformat, formatsort, limit)

    def add_debate_ranking_columns(self, debates, standings):
        def formatsort(x):
            return x[0] or 99999
        return self._add_debate_standing_columns(debates, standings, 'iterrankings',
                'rankings_info', rankingformat, formatsort)

    def add_debate_side_history_columns(self, debates, round):
        # Teams should be prefetched in debates, so don't use a new Team queryset to collate teams
        teams_by_side = [[d.get_team(side) for d in debates] for side in self.tournament.sides]
        all_teams = [team for d in debates for team in d.teams]
        side_histories = get_side_history(all_teams, self.tournament.sides, round.seq)

        for i, (side, teams) in enumerate(zip(self.tournament.sides, teams_by_side)):
            name = _("side history<br>\n(number of times the team has been on each side before this round)")
            # Translators: Abbreviation for "side history"
            abbr = _("SH")
            header = self._prepend_side_header(side, name, abbr)
            cells = self._side_history_by_team(side_histories, teams)
            if i == 0:
                for cell in cells:
                    cell['class'] = 'highlight-col'
            self.add_column(header, cells)


class BasePositionBalanceReportTableBuilder(BaseDrawTableBuilder):
    """Really more of a mixin than a builder, just adds some common
    functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exponent = self.tournament.pref('bp_position_cost_exponent')

        cost_pref = self.tournament.pref('bp_position_cost')
        α = self.tournament.pref('bp_renyi_order')  # noqa: N806
        if cost_pref == "entropy":
            self.position_cost_func = BPHungarianDrawGenerator.get_entropy_position_cost_function(α)
        else:
            self.position_cost_func = getattr(BPHungarianDrawGenerator, BPHungarianDrawGenerator.POSITION_COST_FUNCTIONS[cost_pref])

    def get_position_cost(self, pos, team):
        before = self.side_histories_before[team.id]
        return self.position_cost_func(pos, before) ** self.exponent

    def get_imbalance_category(self, team):
        """Returns the highlighting category for the team. Requires
        `self.side_histories_before` and `self.side_histories_now` to be
        populated.

        Categories work like this:
         - Teams that sunk from ideal to non-ideal: "danger"
         - Teams that could have gone from non-ideal to ideal, but didn't: "danger"
         - Teams that were so imbalanced last round that they are still non-ideal,
           but still did the best they could: "warning"
         - Teams that resolved a previous imbalance: "success"
         - Teams that were ideal both before and now: None

        "Ideal" means that their history is as even as possible, i.e., the
        maximum and minimum number in the history differ by at most 1.
        """
        before = self.side_histories_before[team.id]
        now = self.side_histories_now[team.id]

        ideal_before = max(before) - min(before) <= 1
        ideal_now = max(now) - min(now) <= 1

        if ideal_before and ideal_now:
            return None
        elif ideal_before and not ideal_now:
            return "danger", "regression", 1
        elif ideal_now and not ideal_before:
            return "success", "resolved", 4
        elif now.count(min(before)) < before.count(min(before)):
            return "warning", "improving", 3
        else:
            return "danger", "still-bad", 2


class PositionBalanceReportSummaryTableBuilder(BasePositionBalanceReportTableBuilder):

    STATUSES = {
        "regression": gettext_lazy("Went from balanced to imbalanced"),
        "resolved": gettext_lazy("Went from imbalanced to balanced"),
        "improving": gettext_lazy("Best improvement possible, still imbalanced"),
        "still-bad": gettext_lazy("Was imbalanced and still imbalanced"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort_key = "cost"

    def build(self, draw, teams, side_histories_before, side_histories_now, standings):
        self.side_histories_before = side_histories_before
        self.side_histories_now = side_histories_now
        self.standings = standings

        # Filter for just those teams that are "noteworthy"
        teams = [team for team in teams if self.get_imbalance_category(team) is not None]
        self.add_team_columns(teams)

        # First metric
        if len(self.standings.metric_keys) == 0:  # special case: no metrics used
            header = {
                'key': "pts",
                'title': "?",
                'tooltip': _("No metrics in the team standings precedence"),
            }
            self.add_column(header, [0] * len(teams))
        else:
            metric_info = next(self.standings.metrics_info())
            header = {
                'key': "pts",  # always use 'pts' to make it more predictable
                'title': force_str(metric_info['abbr']),
                'tooltip': force_str(metric_info['name']),
            }
            cells = []
            infos = self.standings.get_standings(teams)
            for info in infos:
                points = info.metrics[metric_info['key']]
                cells.append({
                    'text': metricformat(points),
                    'sort': points,
                })
            self.add_column(header, cells)

        # Sides
        sides_lookup = {dt.team_id: dt.side for debate in draw
                for dt in debate.debateteam_set.all()}
        sides = [sides_lookup[team.id] for team in teams]
        poses = [self.tournament.sides.index(side) for side in sides]  # used later
        names = {side: get_side_name(self.tournament, side, 'abbr') for side in self.tournament.sides}
        header = {'key': "side", 'title': _("Side"),
                  'tooltip': _("Position this round")}
        self.add_column(header, [names[side] for side in sides])

        # Side counts before and now
        header = {'key': "before", 'title': _("Before"),
                  'tooltip': _("Side history before this round")}
        cells = self._side_history_by_team(self.side_histories_before, teams)
        self.add_column(header, cells)

        header = {'key': "after", 'title': _("After"),
                  'tooltip': _("Side history after this round")}
        side_histories_now_highlighted = []
        for team, pos in zip(teams, poses):
            history = [str(x) for x in self.side_histories_now[team.id]]
            history[pos] = "<strong>" + history[pos] + "</strong>"
            history_str = self.side_history_separator.join(history)
            side_histories_now_highlighted.append(history_str)
        self.add_column(header, side_histories_now_highlighted)

        # Position cost
        header = {'key': "cost", 'title': _("Cost"), 'tooltip': _("Position cost")}
        cells = [metricformat(self.get_position_cost(pos, team)) for pos, team in zip(poses, teams)]
        self.add_column(header, cells)

        # Status
        cells = []
        for team in teams:
            style, category, sort = self.get_imbalance_category(team)
            cells.append({
                'text': self.STATUSES[category],
                'sort': sort,
                'class': 'text-' + style,
            })
        self.add_column({'key': 'status', 'title': _("Status")}, cells)

        # Sort by points as secondary sort (will be sorted by cost in Vue)
        self.data.sort(key=lambda x: x[1].get('sort', 0), reverse=True)


class PositionBalanceReportDrawTableBuilder(BasePositionBalanceReportTableBuilder):

    def build(self, debates, teams, side_histories_before, side_histories_now, standings):
        self.debates = debates
        self.teams = teams
        self.side_histories_before = side_histories_before
        self.side_histories_now = side_histories_now
        self.standings = standings

        self.add_permitted_points_column()

        # Just act as if all sides are confirmed (i.e. ignore the sides_confirmed field)
        # If any sides aren't confirmed, there will be a warning on the page.
        for side in self.tournament.sides:
            self.add_all_columns_for_team(side)

        self.highlight_rows_by_column_value(column=0) # highlight first row of a new bracket

    def add_permitted_points_column(self):
        if len(self.standings.metric_keys) == 0:  # special case: no metrics used
            points = [0] * len(self.standings)
        else:
            first_metric = self.standings.metric_keys[0]
            points = [info.metrics[first_metric] for info in self.standings]
            points.sort(reverse=True)

        pref = self.tournament.pref('bp_pullup_distribution')
        define_rooms_func = getattr(BPHungarianDrawGenerator, BPHungarianDrawGenerator.DEFINE_ROOM_FUNCTIONS[pref])
        rooms = define_rooms_func(points)
        data = [sorted(allowed, reverse=True) for level, allowed in rooms]
        cells = []
        for datum in data:
            strs = [metricformat(x) for x in datum]
            strs[0] = "<strong>%s</strong>" % strs[0]
            cells.append(", ".join(strs))
        header = {
            'key': "room",
            'icon': "bar-chart",
            'tooltip': _("Teams with this many points are permitted in this debate<br>\n(bracket in bold)"),
        }
        self.add_column(header, cells)

    def add_all_columns_for_team(self, side):
        teams = [debate.get_team(side) for debate in self.debates]
        side_abbr = get_side_name(self.tournament, side, 'abbr')

        self.add_team_columns(teams, key=side_abbr, show_emoji=False)

        # Highlight the team column
        for row in self.data:
            row[-1]['class'] = 'highlight-col'

        # Points of team
        if len(self.standings.metric_keys) == 0:  # special case: no metrics used
            header = {
                'key': "pts" + side_abbr,
                'tooltip': _("No metrics in the team standings precedence"),
                'icon': 'star',
            }
            self.add_column(header, [0] * len(teams))
        else:
            metric_info = next(self.standings.metrics_info())
            header = {
                'key': "pts" + side_abbr,  # always use 'pts' to make it more predictable
                'tooltip': _("%(team)s: %(metric)s") % {'team': side_abbr, 'metric': metric_info['name']},
                'icon': 'star',
            }
            infos = self.standings.get_standings(teams)
            self.add_column(header, [metricformat(info.metrics[metric_info['key']]) for info in infos])

        # Side history after last round
        header = self._prepend_side_header(side, _("side history before this round"), _("Sides"), text_only=True)
        cells = self._side_history_by_team(self.side_histories_before, teams)
        self.add_column(header, cells)

        # Position cost incurred, post-weighting
        header = self._prepend_side_header(side, _("position cost"), _("Cost"), text_only=True)
        pos = self.tournament.sides.index(side)
        cells = [metricformat(self.get_position_cost(pos, team)) for team in teams]
        self.add_column(header, cells)

        # Highlight according to category
        for row, team in zip(self.data, teams):
            category = self.get_imbalance_category(team)
            if category is None:
                continue
            for cell in row[-4:]:
                cell['class'] = cell.get('class', '') + ' table-' + category[0]
