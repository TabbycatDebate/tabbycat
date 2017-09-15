from django.utils.html import format_html
from django.utils.translation import ugettext as _

from participants.utils import get_side_counts
from standings.templatetags.standingsformat import metricformat, rankingformat
from tournaments.utils import get_side_name
from utils.tables import TabbycatTableBuilder


class AdminDrawTableBuilder(TabbycatTableBuilder):

    def highlight_rows_by_column_value(self, column):
        highlighted_rows = [i for i in range(1, len(self.data))
                if self.data[i][column] != self.data[i-1][column]]
        for i in highlighted_rows:
            self.data[i] = [self._convert_cell(cell) for cell in self.data[i]]
            for cell in self.data[i]:
                cell['class'] = cell.get('class', '') + ' highlight-row'

    def add_room_rank_columns(self, debates):
        header = {
            'key': _("Room rank"),
            'icon': 'bar-chart-2',
            'tooltip': _("Room rank of this debate"),
        }
        self.add_column(header, [debate.room_rank for debate in debates])

    def add_debate_bracket_columns(self, debates):
        header = {
            'key': _("Bracket"),
            'icon': 'bar-chart-2',
            'tooltip': _("Bracket of this debate"),
        }

        def _fmt(x):
            if int(x) == x:
                return int(x)
            return x

        self.add_column(header, [_fmt(debate.bracket) for debate in debates])

    def add_debate_team_columns(self, debates):
        all_sides_confirmed = all(debate.sides_confirmed for debate in debates)  # should already be fetched

        for i, side in enumerate(self.tournament.sides, start=1):
            side_abbr = get_side_name(self.tournament, side, 'abbr')

            team_data = []
            for debate in debates:
                team = debate.get_team(side)
                subtext = None if (all_sides_confirmed or not debate.sides_confirmed) else side_abbr
                team_data.append(self._team_cell(team, subtext=subtext))

            key = side_abbr if all_sides_confirmed else _("Team %(num)d") % {'num': i}
            self.add_column(key, team_data)

    def _debate_standings_headers(self, standings, info_method):
        info_list = getattr(standings, info_method)()
        headers = []
        for info in info_list:
            for side in self.tournament.sides:
                # Translators: e.g. "Affirmative: Rank", "Government: Draw strength",
                # "Opening government: Total speaker score", "Closing opposition: Number of firsts"
                tooltip = _("%(side_name)s: %(metric_name)s") % {
                    'side_name': get_side_name(self.tournament, side, 'full'),
                    'metric_name': info['name'].capitalize(),
                }
                tooltip = tooltip.capitalize()
                key = format_html("{}<br>{}", get_side_name(self.tournament, side, 'abbr'), info['abbr'])

                header = {
                    'key': key,  # no need to translate
                    'tooltip': tooltip,
                    'icon': info['icon'],
                    'text': key if info['icon'] is None else None
                }
                headers.append(header)

        return headers

    def _add_debate_standing_columns(self, debates, standings, itermethod, infomethod, formattext, formatsort):
        standings_by_debate = [standings.get_standings(
                [d.get_team(side) for side in self.tournament.sides]) for d in debates]
        cells = []

        for debate in standings_by_debate:
            metrics_by_team = []  # will be list of lists, one list of metrics for each side
            for i, standing in enumerate(debate):
                metrics = []  # metrics for this team
                for metric in getattr(standing, itermethod)():
                    metrics.append({'text': formattext(metric), 'sort': formatsort(metric)})
                if i == 0:
                    for cell in metrics:
                        cell['class'] = 'highlight-col'
                metrics_by_team.append(metrics)
            cells.append([y for x in zip(*metrics_by_team) for y in x])

        headers = self._debate_standings_headers(standings, infomethod)
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
        return self._add_debate_standing_columns(debates, standings, 'itermetrics',
                'metrics_info', metricformat, formatsort)

    def add_debate_ranking_columns(self, debates, standings):
        def formatsort(x):
            return x[0] or 99999
        return self._add_debate_standing_columns(debates, standings, 'iterrankings',
                'rankings_info', rankingformat, formatsort)

    def add_debate_side_counts(self, debates, round):
        # Note that the spaces used in the separator are nonbreaking spaces, not normal spaces
        separator = " " if self.tournament.pref('teams_in_debate') == 'bp' else " / "

        for i, side in enumerate(self.tournament.sides):
            teams = [d.get_team(side) for d in debates]

            # Translators: e.g. team would be "negative team" or "affirmative team".
            tooltip = _("Number of times this %(team)s has been on each side") % {
                'team': get_side_name(self.tournament, side, "team"),
            }
            # Translators: "SC" stands for "side count"
            key = format_html("{}<br>{}", get_side_name(self.tournament, side, 'abbr'), _("SC"))
            header = {'key': key, 'tooltip': tooltip, 'text': key}

            sides = self.tournament.sides
            side_counts = get_side_counts(teams, sides, round.seq)
            cells = [{'text': separator.join(map(str, side_counts[team.id]))} for team in teams]
            if i == 0:
                for cell in cells:
                    cell['class'] = 'highlight-col'
            self.add_column(header, cells)
