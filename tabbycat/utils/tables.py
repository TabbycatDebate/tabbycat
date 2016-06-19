from adjallocation.models import DebateAdjudicator
from breakqual.models import BreakingTeam
from draw.models import Debate
from standings.templatetags.standingsformat import metricformat, rankingformat
from utils.misc import reverse_tournament

from .mixins import SuperuserRequiredMixin


class BaseTableBuilder:
    """Class for building tables that can be easily inserted into Vue tables,
    Designed to be used with VueTableMixin.

    In the docstrings for this class:
    - A *header dict* is a dict that contains a value under `"key"` that is a
      string, and may optionally contain entries under `"tooltip"`, `"icon"`,
      `"visible-sm"`, `"visible-md"` and `"visible-lg"`.
    - A *cell dict* is a dict that contains a value under `"text"` that is a
      string, and may optionally contain entries under `"sort"`, `"icon"`,
      `"emoji"`, `"tooltip"` and `"link"`.

    """

    def __init__(self, **kwargs):
        self.headers = []
        self.data = []
        self.title = kwargs.get('title', "")
        self.table_class = kwargs.get('table_class', "")
        self.sort_key = kwargs.get('sort_key', '')
        self.sort_order = kwargs.get('sort_order', '')

    @staticmethod
    def _convert_header(header):
        return {'key': header} if isinstance(header, str) else header

    @staticmethod
    def _convert_cell(cell):
        if isinstance(cell, int):
            return {'text': str(cell)}
        if isinstance(cell, str):
            return {'text': cell}
        return cell

    def add_column(self, header, data):
        """Adds a column to the table.

        - `header` must be either a string or a header dict (see class docstring).
        - `data` must be a list of cells (in the column). Each cell should
          either be a string or a cell dict (see class docstring). If this is
          not the first column, then there must be as many elements in `data` as
          there are in the existing columns.
        """
        if len(self.data) > 0 and len(data) != len(self.data):
            raise ValueError("data contains {new:d} rows, existing table has {existing:d}".format(
                new=len(data), existing=len(self.data)))

        header = self._convert_header(header)
        self.headers.append(header)

        data = map(self._convert_cell, data)
        if len(self.data) == 0:
            self.data = [[cell] for cell in data]
        else:
            for row, cell in zip(self.data, data):
                row.append(cell)

    def add_boolean_column(self, header, data):
        """Convenience function for adding a column based on boolean data.

        - `header` must be either a string or a header dict.
        - `data` must be an iterable of booleans.
        """
        cells = [{
            'icon': 'glyphicon-ok' if datum else '',
            'sort':  1 if datum else 2,
        } for datum in data]
        self.add_column(header, cells)

    def add_columns(self, headers, data):
        """Adds columns to the table.

        This method is intended for situations where it is easier to process
        data by row while adding it to the table, than it is to process data
        by column. In the latter case, use `add_column()` instead.

        - `headers` must be a list of strings or header dicts (or both).
        - `data` must be a list of lists of cells, where each cell is a string
          or cell dict. Each inner list corresponds to a row, and all inner
          lists must contain the same number of elements, which must also match
          the number of elements in `headers`. If there are no existing columns
          in the table, then there must be as many inner lists as there are
          existing columns.
        """
        if len(self.data) > 0 and len(data) != len(self.data):
            raise ValueError("data contains {new:d} rows, existing table has {existing:d}".format(
                new=len(data), existing=len(self.data)))

        headers = map(self._convert_header, headers)
        self.headers.extend(headers)

        if len(self.data) == 0:
            self.data = [[self._convert_cell(cell) for cell in row] for row in data]
        else:
            for row, cells in zip(self.data, data):
                cells = map(self._convert_cell, cells)
                row.extend(cells)

    def jsondict(self):
        """Returns the JSON dict for the table."""
        return {
            'head': self.headers,
            'data': self.data,
            'title': self.title,
            'class': self.table_class,
            'sort_key': self.sort_key,
            'sort_order': self.sort_order
        }


class TabbycatTableBuilder(BaseTableBuilder):
    """Extends TableBuilder to add convenience functions specific to
    Tabbycat."""

    ADJ_SYMBOLS = {
        DebateAdjudicator.TYPE_CHAIR: " Ⓒ",
        DebateAdjudicator.TYPE_PANEL: "",
        DebateAdjudicator.TYPE_TRAINEE: " Ⓣ",
    }

    def __init__(self, view=None, **kwargs):
        """Constructor.
        - If `tournament` is specified, it becomes the default tournament for
          the builder.
        - If `admin` is True (default is False), then relevant links will go
          to the admin version rather than the public version.
        - If `view` is specified, then `tournament` and `admin` are inferred
          from `view`. This option is provided for convenience.
        """
        if 'tournament' not in kwargs and hasattr(view, 'get_tournament'):
            self.tournament = view.get_tournament()
        else:
            self.tournament = kwargs.get('tournament')

        if 'admin' not in kwargs and isinstance(view, SuperuserRequiredMixin):
            self.admin = True
        else:
            self.admin = kwargs.get('admin', False)

        return super().__init__(**kwargs)

    def add_round_column(self, rounds, key="Round"):
        data = [{
            'sort': round.seq,
            'text': round.abbreviation,
            'tooltip': round.name,
        } for round in rounds]
        self.add_column(key, data)

    def add_adjudicator_columns(self, adjudicators, hide_institution=False, subtext=None):

        if subtext is 'institution':
            self.add_column("Name", [{
                'text': adj.name,
                'subtext': adj.institution.code
            } for adj in adjudicators])
        else:
            self.add_column("Name", [adj.name for adj in adjudicators])

        if self.tournament.pref('show_institutions') and not hide_institution:
            self.add_column("Institution", [adj.institution.code for adj in adjudicators])

        adjcore_header = {
            'tooltip': "Member of the Adjudication Core",
            'icon': 'glyphicon-sunglasses',
        }
        self.add_boolean_column(adjcore_header, [adj.adj_core for adj in adjudicators])

        independent_header = {
            'tooltip': "Independent Adjudicator",
            'icon': 'glyphicon-knight',
        }
        self.add_boolean_column(independent_header, [adj.independent for adj in adjudicators])

        if self.tournament.pref('show_unaccredited'):
            accreddited_header = {
                'tooltip': "Is Accredited",
                'icon': 'glyphicon-leaf',
            }
            self.add_boolean_column(accreddited_header, [adj.novice for adj in adjudicators])

    def add_debate_adjudicators_column(self, debates, key="Adjudicators", show_splits=False):
        data = []
        for debate in debates:
            adj_strings = []

            if debate.confirmed_ballot and show_splits and (self.admin or self.tournament.pref('show_splitting_adjudicators')):
                for adjtype, adj, split in debate.confirmed_ballot.ballot_set.adjudicator_results:
                    adj_string = adj.name + self.ADJ_SYMBOLS[adjtype]
                    if split:
                        adj_string = "<span class='text-danger'>" + adj_string + " 💢</span>"
                    adj_strings.append(adj_string)
            else:
                for adjtype, adj in debate.adjudicators:
                    adj_strings.append(adj.name + self.ADJ_SYMBOLS[adjtype])

            data.append(", ".join(adj_strings))

        self.add_column(key, data)

    def add_motion_column(self, motions, key="Motion", show_order=False):
        if show_order and self.tournament.pref('enable_motions'):
            self.add_column("Order", [motion.seq for motion in motions])

        motion_data = [{
            'text': motion.reference,
            'tooltip': motion.text,
        } for motion in motions]
        self.add_column(key, motion_data)

    def add_team_columns(self, teams, break_categories=False, show_speakers=False,
            hide_institution=False, hide_emoji=False, key="Team"):

        team_data = [{
            'text': team.short_name,
            'emoji': team.emoji if self.tournament.pref('show_emoji') and not hide_emoji else None,
            'sort': team.short_name,
            'tooltip': [" " + s.name for s in team.speakers]
                if self.tournament.pref('show_speakers_in_draw') or show_speakers else None # noqa
        } for team in teams]
        self.add_column(key, team_data)

        if break_categories:
            self.add_column("Categories", [", ".join(bc.name for bc in team.break_categories) for team in teams])

        if self.tournament.pref('show_institutions') and not hide_institution:
            self.add_column("Institution", [team.institution.code for team in teams])

    def add_speaker_columns(self, speakers, key="Name"):
        self.add_column(key, [speaker.name for speaker in speakers])
        if self.tournament.pref('show_novices'):
            novice_header = {
                'key': "Novice",
                'icon': 'glyphicon-leaf',
                'tooltip': "Novice Status",
            }
            self.add_boolean_column(novice_header, [speaker.novice for speaker in speakers])

    def add_debate_bracket_columns(self, debates):
        bracket_header = {
            'key': "Bracket",
            'icon': 'glyphicon-stats',
            'tooltip': 'Bracket of this debate'
        }
        bracket_data = [{'text': debate.bracket} for debate in debates]
        self.add_column(bracket_header, bracket_data)

    def add_debate_venue_columns(self, debates, with_times=False):
        if self.tournament.pref('enable_divisions'):
            self.add_column("Division", [debate.division.name for debate in debates])

        venue_header = {
            'key': "Venue",
            'icon': 'glyphicon glyphicon-map-marker',
        }
        if self.tournament.pref('enable_venue_groups'):
            venue_data = [
                debate.division.venue_group.short_name if debate.division
                else (debate.venue.group.short_name + debate.venue.name)
                for debate in debates
            ]
        else:
            venue_data = [debate.venue.name for debate in debates]
        self.add_column(venue_header, venue_data)

        if with_times and self.tournament.pref('enable_debate_scheduling'):
            times_headers = ["Date", "Time"]
            times_data = []
            for debate in debates:
                if debate.aff_team.type == Debate.TYPE_BYE or debate.neg_team.type == Debate.TYPE_BYE:
                    times_data.append(["", "Bye"])
                elif debate.result_status == Debate.STATUS_POSTPONED:
                    times_data.append(["", "Postponed"])
                elif debate.confirmed_ballot.forfeit:
                    times_data.append(["", "Forfeit"])
                else:
                    times_data.append([debate.time.strftime("D jS F"), debate.time.strftime("h:i A")])
            self.add_columns(times_headers, times_data)

    def add_draw_conflicts(self, draw):
        conflicts_header = {'key': "Conflicts/Flags"}
        conflicts_data = [{
            'text': debate.draw_conflicts + debate.flags_all,
            'class': 'text-danger'
        } for debate in draw]
        self.add_column(conflicts_header, conflicts_data)

    def add_breakrank_columns(self, teams, round):
        breakrank_header = {'key': 'Breaking'}
        breakrank_data = [{
            'text': BreakingTeam.objects.get(
                break_category=round.break_category,
                team=team.id).break_rank
        } for team in teams]
        self.add_column(breakrank_header, breakrank_data)

    def add_subrank_columns(self, draw, key):
        subrank_header = {'key': key}
        subrank_data = []
        for d in draw:
            sub_rank = d.aff_subrank[0] if key is 'ASR' else d.neg_subrank[0]
            sub_rank += "=" if key is 'ASR' and d.aff_subrank[1] else ''
            sub_rank += "=" if key is 'NSR' and d.neg_subrank[1] else ''
            subrank_data.append({'text': sub_rank})
        self.add_column(subrank_header, subrank_data)

    def add_ranking_columns(self, standings):
        headers = [{
            'key': info['abbr'],
            'tooltip': info['name'].title(),
            'glyphicon': info['glyphicon'],
        } for info in standings.rankings_info()]
        data = []
        for standing in standings:
            data.append([{
                'text': rankingformat(ranking),
                'sort': ranking[0] or "99999",
            } for ranking in standing.iterrankings()])
        self.add_columns(headers, data)

    def add_metric_columns(self, standings):
        headers = [{
            'key': info['abbr'],
            'tooltip': info['name'].title(),
            'glyphicon': info['glyphicon'],
        } for info in standings.metrics_info()]
        data = [list(map(metricformat, standing.itermetrics())) for standing in standings]
        self.add_columns(headers, data)

    def add_affs_count(self, teams, round, type):
        affs_header = {
            'key':  'aaffs' if type is 'aff' else 'naffs',
            'tooltip': 'Number of times the current ' + type + ' has been in the affirmative position before'
        }
        affs_data = [{
            'text': t.get_aff_count(round.seq) if round.prev else '',
        } for t in teams]
        self.add_columns(affs_header, affs_data)

    # def add_draw_metric_columns(self, teams, round, standings):
    #     aff_standings = [standings.get_standing(t) for t in teams]

    #     if round.is_break_round:
    #         self.add_breakrank_columns(teams, round)
    #     else:
    #         if "points" in standings.metric_keys:
    #             aff_is_pullup = abs(aff_standing.metrics["points"] - debate.bracket) >= 1

    #         aff_subrank = aff_standing.rankings["subrank"]

    #     # debate.metrics = [(a, n) for a, n in zip(aff_standing.itermetrics(), neg_standing.itermetrics())]

    def add_debate_ballot_link_column(self, debates):
        if self.tournament.pref('ballots_released'):
            ballot_links_header = {'key': "Ballot", 'icon': 'glyphicon-search'}
            ballot_links_data = [{
                'text': "View Ballot",
                'link': reverse_tournament('public_ballots_view', self.tournament, kwargs={'debate_id': debate.id})
            } if debate else "" for debate in debates]
            self.add_column(ballot_links_header, ballot_links_data)
