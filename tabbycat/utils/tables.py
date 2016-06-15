import json

from adjallocation.models import DebateAdjudicator

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

    def __init__(self):
        self.headers = []
        self.data = []

    @staticmethod
    def _convert_header(header):
        return {'key': header} if isinstance(header, str) else header

    @staticmethod
    def _convert_cell(cell):
        return {'text': cell} if isinstance(cell, str) else cell

    def add_column(self, header, data):
        """Adds a column to the table.

        - `header` must be either a string or a header dict (see class docstring).
        - `data` should be a list of cells (in the column). Each cell should
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
        for row, cell in zip(self.data, data):
            row.append(cell)

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

        for row, cells in zip(self.data, data):
            cells = map(self._convert_cell, cells)
            row.extend(cells)

    def json(self):
        """Returns the JSON string for the table."""
        return json.dumps({'head': self.headers, 'data': self.data})


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

    def add_round_column(self, rounds, key="Round"):
        data = [{
            'sort': round.seq,
            'text': round.abbreviation,
            'tooltip': round.name,
        } for round in rounds]
        self.add_column(key, data)

    def add_adjudicator_columns(self, adjudicators, hide_institution=False):
        self.add_column("Name", [adj.name for adj in adjudicators])

        if self.tournament.pref('show_institutions') and not hide_institution:
            self.add_column("Institution", [adj.institution.code for adj in adjudicators])

        adjcore_header = {'tooltip': "Member of the Adjudication Core", 'icon': 'glyphicon-sunglasses'}
        adjcore_data = [{
            'icon': 'glyphicon-ok' if adj.adj_core else '',
            'sort': int(adj.adj_core),
        } for adj in adjudicators]
        self.add_column(adjcore_header, adjcore_data)

        independent_header = {'tooltip': "Independent Adjudicator", 'icon': 'glyphicon-knight'}
        independent_data = [{
            'icon': 'glyphicon-ok' if adj.independent else '',
            'sort': int(adj.independent),
        } for adj in adjudicators]
        self.add_column(independent_header, independent_data)

    def add_debate_adjudicators_column(self, debates, key="Adjudicators", show_splits=False):
        data = []
        for debate in debates:
            adj_strings = []

            if debate.confirmed_ballot and show_splits:
                for adjtype, adj, split in debate.confirmed_ballot.ballot_set.adjudicator_results:
                    adj_string = adj.name + self.ADJ_SYMBOLS[adjtype]
                    if split:
                        adj_string = "<span class='text-danger'>" + adj_string + "</span>"
                    adj_strings.append(adj_string)
            else:
                for adjtype, adj in debate.adjudicators:
                    adj_strings.append(adj.name + self.ADJ_SYMBOLS[adjtype])

            data.append(", ".join(adj_strings))

        self.add_column(key, data)

    def add_motion_column(self, motions, key="Motion"):
        if self.tournament.pref('enable_motions'):
            self.add_column("Order", [motion.seq for motion in motions])

        motion_data = [{
            'text': motion.reference,
            'tooltip': motion.text,
        } for motion in motions]
        self.add_column(key, motion_data)

    def add_team_column(self, teams, break_categories=False, show_speakers=False,
            hide_institution=False, key="Team"):

        team_data = [{
            'text': team.short_name,
            'emoji': team.emoji if self.tournament.pref('show_emoji') else None,
            'sort': team.short_name,
            'tooltip': [" " + s.name for s in team.speakers]
                if self.tournament.pref('show_speakers_in_draw') or show_speakers else None # noqa
        } for team in teams]
        self.add_column(key, team_data)

        if break_categories:
            self.add_column("Categories", [", ".join(bc.name for bc in team.break_categories) for team in teams])

        if self.tournament.pref('show_institutions') and not hide_institution:
            self.add_column("Institution", [team.institution.code for team in teams])
