import logging
import warnings

from django.contrib.auth.models import AnonymousUser
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db.models import Exists, OuterRef, Prefetch
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import SafeString
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from adjallocation.allocation import AdjudicatorAllocation
from draw.generator import DRAW_FLAG_DESCRIPTIONS
from draw.models import Debate
from options.utils import use_team_code_names
from results.models import BallotSubmission
from results.result import get_result_class
from standings.templatetags.standingsformat import metricformat, rankingformat
from tournaments.mixins import SingleObjectByRandomisedUrlMixin
from tournaments.utils import get_side_name
from users.permissions import has_permission, Permission
from utils.misc import reverse_round, reverse_tournament

from .mixins import AdministratorMixin

logger = logging.getLogger(__name__)
_draw_flags_dict = dict(DRAW_FLAG_DESCRIPTIONS)


def escape_if_unsafe(s):
    return s if type(s) is SafeString else escape(s)


class BaseTableBuilder:
    """Class for building tables that can be easily inserted into Vue tables,
    Designed to be used with VueTableTemplateView.

    In the docstrings for this class:
    - A *header dict* is a dict that contains a value under `"key"` that is a
      string, and may optionally contain entries under `"tooltip"`, `"icon"`,
      `"visible-sm"`, `"visible-md"` and `"visible-lg"`.
    - A *cell dict* is a dict that contains a value under `"text"` that is a
      string, and may optionally contain entries under `"sort"`, `"icon"`,
      `"emoji"`, `"popover"` and `"link"`.

    """

    def __init__(self, **kwargs):
        self.headers = []
        self.data = []
        self.title = kwargs.get('title', "")
        self.subtitle = kwargs.get('subtitle', "")
        self.table_class = kwargs.get('table_class', "")
        self.sort_key = kwargs.get('sort_key', '')
        self.sort_order = kwargs.get('sort_order', '')
        self.empty_title = kwargs.get('empty_title', _("No Data Available"))

    @staticmethod
    def _convert_header(header):
        if isinstance(header, dict):
            header['key'] = force_str(header['key'])
            return header
        else:
            # not sure why warnings module isn't working, so also use logger.warning to be annoying
            warnings.warn("Plain-text headers are deprecated, use a dict with key and title instead", stacklevel=3)
            return {'key': force_str(header), 'title': force_str(header)}

    @staticmethod
    def _convert_cell(cell):
        if isinstance(cell, dict):
            if 'text' in cell:
                cell['text'] = force_str(cell['text'])
            return cell
        else:
            cell_dict = {}
            if isinstance(cell, int) or isinstance(cell, float):
                cell_dict['sort'] = cell
            cell_dict['text'] = force_str(cell)
            return cell_dict

    def add_column(self, header, data):
        """Adds a column to the table.

        - `header` must be either a string or a header dict (see class docstring).
        - `data` must be a list of cells (in the column). Each cell should
          either be a string or a cell dict (see class docstring). If this is
          not the first column, then there must be as many elements in `data` as
          there are in the existing columns.
        """
        if 0 < len(self.data) != len(data):
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
            'icon': 'check' if datum else '',
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
        if 0 < len(self.data) != len(data):
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
            'title': force_str(self.title),
            'subtitle': force_str(self.subtitle),
            'empty_title': force_str(self.empty_title),
            'class': self.table_class,
            'sort_key': self.sort_key,
            'sort_order': self.sort_order,
        }


class FakeRequest(object):
    user = AnonymousUser()


class TabbycatTableBuilder(BaseTableBuilder):
    """Extends TableBuilder to add convenience functions specific to
    Tabbycat."""

    ADJ_SYMBOLS = {
        AdjudicatorAllocation.POSITION_CHAIR: _("Ⓒ"),
        AdjudicatorAllocation.POSITION_ONLY: _("Ⓒ"),
        AdjudicatorAllocation.POSITION_TRAINEE: _("Ⓣ"),
    }

    ADJ_POSITION_NAMES = {
        AdjudicatorAllocation.POSITION_CHAIR: _("chair"),
        AdjudicatorAllocation.POSITION_PANELLIST: _("panellist"),
        AdjudicatorAllocation.POSITION_TRAINEE: _("trainee"),
    }

    BLANK_TEXT = _("—")
    REDACTED_CELL = {'text': "<em>" + _("Redacted") + "</em>", 'class': 'no-wrap'}

    def __init__(self, view=None, **kwargs):
        """Constructor.
        - If `tournament` is specified, it becomes the default tournament for
          the builder.
        - If `admin` is True (default is False), then relevant links will go
          to the admin version rather than the public version.
        - If `view` is specified, then `tournament` and `admin` are inferred
          from `view`. This option is provided for convenience.
        """
        if 'tournament' not in kwargs and hasattr(view, 'tournament'):
            self.tournament = view.tournament
        else:
            self.tournament = kwargs.get('tournament')

        if 'admin' not in kwargs and isinstance(view, AdministratorMixin):
            self.admin = True
        else:
            self.admin = kwargs.get('admin', False)

        self.user = kwargs.get('user', getattr(view, 'request', FakeRequest()).user)

        if isinstance(view, SingleObjectByRandomisedUrlMixin):
            self.private_url = True
            self.private_url_key = view.kwargs.get('url_key')
        else:
            self.private_url = kwargs.get('private_url', False)

        if self.tournament.pref('teams_in_debate') > 2:
            self._result_cell = self._result_cell_bp
        else:
            self._result_cell = self._result_cell_two

        return super().__init__(**kwargs)

    @property
    def _show_record_links(self):
        return self.admin or self.tournament.pref('public_record')

    @property
    def _show_speakers_in_draw(self):
        return self.tournament.pref('show_speakers_in_draw') or self.admin

    @property
    def _use_team_code_names(self):
        return use_team_code_names(self.tournament, self.admin, user=self.user)

    def _team_short_name(self, team):
        """Returns the appropriate short name for the team, accounting for team code name preference."""
        if self._use_team_code_names:
            return escape(team.code_name)
        else:
            return escape(team.short_name)

    def _team_long_name(self, team):
        """Returns the appropriate long name for the team, accounting for team code name preference."""
        if self._use_team_code_names:
            return escape(team.code_name)
        else:
            return escape(team.long_name)

    def _adjudicator_record_link(self, adj, suffix=""):
        adj_short_name = adj.get_public_name(self.tournament).split(" ")[0]
        if self.admin:
            return {
                'text': _("View %(a)s's %(d)s Record") % {'a': escape_if_unsafe(adj_short_name), 'd': suffix},
                'link': reverse_tournament('participants-adjudicator-record',
                    self.tournament, kwargs={'pk': adj.pk}),
            }
        elif self.tournament.pref('public_record'):
            return {
                'text': _("View %(a)s's %(d)s Record") % {'a': escape_if_unsafe(adj_short_name), 'd': suffix},
                'link': reverse_tournament('participants-public-adjudicator-record',
                    self.tournament, kwargs={'pk': adj.pk}),
            }
        else:
            return {'text': '', 'link': False}

    def _team_record_link(self, team):
        if self.admin:
            return {
                'text': _("View %(team)s's Record") % {'team': self._team_short_name(team)},
                'link': reverse_tournament('participants-team-record', self.tournament, kwargs={'pk': team.pk}),
            }
        elif self.tournament.pref('public_record'):
            return {
                'text': _("View %(team)s's Record") % {'team': self._team_short_name(team)},
                'link': reverse_tournament('participants-public-team-record', self.tournament, kwargs={'pk': team.pk}),
            }
        else:
            return {'text': '', 'link': False}

    def _team_cell(self, team, show_emoji=False, subtext=None, highlight=False):
        cell = {
            'text': self._team_short_name(team),
            'emoji': escape(team.emoji) if team.emoji and show_emoji and self.tournament.pref('show_emoji') else None,
            'sort': self._team_short_name(team),
            'class': 'team-name no-wrap' if len(self._team_short_name(team)) < 18 else 'team-name',
            'popover': {'title': self._team_long_name(team), 'content': []},
        }

        if highlight:
            cell['class'] += ' font-weight-bold table-secondary'
        if subtext:
            cell['subtext'] = subtext

        if (self.tournament.pref('team_code_names') == 'all-tooltips' or  # code names in tooltips
                (self.tournament.pref('team_code_names') == 'admin-tooltips-code' and self.admin)):
            cell['popover']['content'].append({'text': _("Code name: <strong>%(name)s</strong>") % {'name': escape(team.code_name)}})
        if self.tournament.pref('team_code_names') == 'admin-tooltips-real' and self.admin:
            cell['popover']['content'].append({'text': _("Real name: <strong>%(name)s</strong>") % {'name': escape(team.short_name)}})

        if self._show_speakers_in_draw:
            if self.admin and has_permission(self.user, Permission.VIEW_ANONYMOUS, self.tournament):
                speakers = ["<span class='admin-redacted'>%s</span>" % escape(s.name) if s.anonymous else escape(s.name) for s in team.speakers]
            else:
                speakers = [self.REDACTED_CELL['text'] if s.anonymous else escape(s.get_public_name(self.tournament)) for s in team.speakers]

            cell['popover']['content'].append({'text': ", ".join(speakers)})
        if self._show_record_links:
            cell['popover']['content'].append(self._team_record_link(team))

        if self.admin and getattr(team, 'anonymise', False):
            cell['class'] += ' admin-redacted'

        return cell

    def _result_cell_class_two(self, win, cell):
        team_name = cell['popover']['title']
        if win is True:
            cell['popover']['title'] = _("%(team)s won") % {'team': team_name}
            cell['icon'] = "chevron-up"
            cell['iconClass'] = "text-success result-icon"
            cell['sort'] = 2
        elif win is False:
            cell['popover']['title'] = _("%(team)s lost") % {'team': team_name}
            cell['icon'] = "chevron-down"
            cell['iconClass'] = "text-danger result-icon"
            cell['sort'] = 1
        else: # None
            cell['popover']['title'] = _("%(team)s—no result") % {'team': team_name}
            cell['icon'] = ""
            cell['sort'] = 0
        return cell

    BP_POINT_ICONS = ("chevrons-down", "chevron-down", "chevron-up", "chevrons-up")
    BP_POINT_ICONCLASSES = ("text-danger result-icon", "text-warning result-icon", "text-info result-icon", "text-success result-icon")

    def _result_cell_class_four(self, points, cell, n_teams):
        team_name = cell['popover']['title']

        if points is None:
            cell['popover']['title'] = _("%(team)s—no result") % {'team': team_name}
            cell['icon'] = ""
            cell['sort'] = 0
            return cell

        cell['popover']['title'] = _("%(team)s placed %(place)s") % {'team': team_name, 'place': ordinal(n_teams - points)}
        if n_teams <= 4:
            cell['icon'] = self.BP_POINT_ICONS[points]
            cell['iconClass'] = self.BP_POINT_ICONCLASSES[points]
        cell['sort'] = points + 1
        return cell

    def _result_cell_class_four_elim(self, advancing, cell):
        team_name = cell['popover']['title']
        if advancing is True:
            cell['popover']['title'] = _("%(team)s is advancing") % {'team': team_name}
            cell['icon'] = "chevron-up"
            cell['iconClass'] = "text-success"
            cell['sort'] = 2
        elif advancing is False:
            cell['popover']['title'] = _("%(team)s was eliminated") % {'team': team_name}
            cell['icon'] = "chevron-down"
            cell['iconClass'] = "text-danger"
            cell['sort'] = 1
        else: # None
            cell['popover']['title'] = _("%(team)s—no result") % {'team': team_name}
            cell['icon'] = ""
            cell['sort'] = 0
        return cell

    def _show_ballots(self, cell, ts, link: str):
        if self.admin:
            cell['popover']['content'].append({
                'text': _("View/edit debate ballot"),
                'link': reverse_tournament(link,
                        self.tournament, kwargs={'pk': ts.ballot_submission_id}),
            })
        elif self.tournament.pref('ballots_released'):
            cell['popover']['content'].append({
                'text': _("View debate ballot"),
                'link': reverse_tournament('results-public-scoresheet-view',
                        self.tournament, kwargs={'pk': ts.debate_team.debate_id}),
            })

    def _result_cell_two(self, ts, compress=False, show_score=False, show_ballots=False):
        if not hasattr(ts, 'debate_team') or not hasattr(ts.debate_team.opponent, 'team'):
            return {'text': self.BLANK_TEXT}

        opp = ts.debate_team.opponent.team
        opp_vshort = '<i class="emoji">' + escape(opp.emoji) + '</i>' if opp.emoji else "…"

        cell = {
            'text': _(" vs %(opposition)s") % {'opposition': opp_vshort if compress else self._team_short_name(opp)},
            'popover': {'content': [], 'title': ''},
            'class': "no-wrap",
        }
        cell = self._result_cell_class_two(ts.win, cell)

        if ts.win is True:
            cell['popover']['title'] = _("Won against %(team)s") % {'team': self._team_long_name(opp)}
        elif ts.win is False:
            cell['popover']['title'] = _("Lost to %(team)s") % {'team': self._team_long_name(opp)}
        else: # None
            cell['popover']['title'] = _("No result for debate against %(team)s") % {'team': self._team_long_name(opp)}

        if show_score and ts.score is not None:
            self._show_score(ts, cell)

        if show_ballots:
            self._show_ballots(cell, ts, "old-results-ballotset-edit")

        if self._show_speakers_in_draw:
            cell['popover']['content'].append({
                'text': ", ".join([escape_if_unsafe(s.get_public_name(self.tournament)) for s in opp.speakers]),
            })

        if self._show_record_links:
            cell['popover']['content'].append(
                self._team_record_link(opp))

        return cell

    def _show_score(self, ts, cell):
        score = ts.score
        if self.tournament.integer_scores(ts.debate_team.debate.round.stage) and score.is_integer():
            score = int(ts.score)
        cell['subtext'] = metricformat(score)
        cell['popover']['content'].append(
            {'text': _("Total speaker score: <strong>%s</strong>") % metricformat(score)})

    def _result_cell_bp(self, ts, compress=False, show_score=False, show_ballots=False):
        if not hasattr(ts, 'debate_team'):
            return {'text': self.BLANK_TEXT}

        other_teams = {dt.side: self._team_short_name(dt.team) for dt in ts.debate_team.debate.debateteam_set.all()}
        n_teams = max(other_teams.keys()) + 1
        other_team_strs = [_("Teams in debate:")]
        for side in range(n_teams):
            if ts.debate_team.debate.sides_confirmed:
                line = _("%(team)s (%(side)s)") % {
                    'team': other_teams.get(side, _("??")),
                    'side': get_side_name(self.tournament, side, 'abbr'),
                }
            else:
                line = other_teams.get(side, _("??"))
            if side == ts.debate_team.side:
                line = "<strong>" + line + "</strong>"
            other_team_strs.append(line)

        cell = {'popover': {
            'content': [{'text': "<br />".join(other_team_strs)}],
            'title': "",
            'class': "no-wrap",
        }}

        if ts.debate_team.debate.round.is_break_round:
            cell = self._result_cell_class_four_elim(ts.win, cell)
            if ts.win is True:
                cell['text'] = _("advancing")
                cell['popover']['title'] = _("Advancing")
            elif ts.win is False:
                cell['text'] = _("eliminated")
                cell['popover']['title'] = _("Eliminated")
            else:
                cell['text'] = "–"
                cell['popover']['title'] = _("No result for debate")
        else:
            cell = self._result_cell_class_four(ts.points, cell, n_teams)
            places = [ordinal(n) for n in reversed(range(1, 5))]
            if ts.points is not None:
                place = places[ts.points] if ts.points < 4 else _("??")
                cell['text'] = place
                cell['popover']['title'] = _("Placed %(place)s") % {'place': place}
            else:
                cell['text'] = "–"
                cell['popover']['title'] = _("No result for debate")

        if show_score and ts.score is not None:
            self._show_score(ts, cell)

        if show_ballots:
            self._show_ballots(cell, ts, "results-ballotset-edit")

        return cell

    def add_tournament_column(self, tournaments):
        header = {
            'key': "tournament", 'icon': 'tag', 'tooltip': _("Tournament"),
        }
        data = [{
            'sort': t.seq, 'text': escape(t.short_name), 'tooltip': escape(t.short_name),
        } for t in tournaments]
        self.add_column(header, data)

    def add_round_column(self, rounds):
        header = {
            'key': "round", 'icon': 'clock', 'tooltip': _("Round"),
        }
        data = [{
            'sort': round.seq, 'text': escape(round.abbreviation), 'tooltip': escape(round.name),
        } for round in rounds]
        self.add_column(header, data)

    def add_adjudicator_columns(self, adjudicators, show_institutions=True,
            show_metadata=True, subtext=None):

        adj_data = []
        for adj in adjudicators:
            if adj.anonymous and not (self.admin and has_permission(self.user, Permission.VIEW_ANONYMOUS, self.tournament)):
                adj_data.append(self.REDACTED_CELL)
            else:
                cell = {'text': escape_if_unsafe(adj.get_public_name(self.tournament))}
                if adj.anonymous:
                    cell['class'] = 'admin-redacted'
                if self._show_record_links:
                    cell['popover'] = {'title': escape_if_unsafe(adj.get_public_name(self.tournament)), 'content': [self._adjudicator_record_link(adj)]}
                if subtext == 'institution' and adj.institution is not None:
                    cell['subtext'] = escape(adj.institution.code)
                adj_data.append(cell)
        self.add_column({'key': 'name', 'tooltip': _("Name"), 'icon': 'user'}, adj_data)

        if show_institutions and self.tournament.pref('show_adjudicator_institutions'):
            self.add_column({
                'key': "institution",
                'icon': 'home',
                'tooltip': _("Institution"),
            }, [escape(adj.institution.code) if adj.institution else self.BLANK_TEXT for adj in adjudicators])

        if show_metadata:
            adjcore_header = {
                'key': 'adjcore',
                'tooltip': _("Member of the Adjudication Core"),
                'icon': 'user-check',
            }
            self.add_boolean_column(adjcore_header, [adj.adj_core for adj in adjudicators])

            independent_header = {
                'key': 'independent',
                'tooltip': _("Independent Adjudicator"),
                'icon': 'user-plus',
            }
            self.add_boolean_column(independent_header, [adj.independent for adj in adjudicators])

        if self.tournament.pref('show_unaccredited'):
            trainee_header = {
                'key': 'accredited',
                'tooltip': _("Always Trainee"),
                'icon': 'user-minus',
            }
            self.add_boolean_column(trainee_header, [adj.trainee for adj in adjudicators])

    def add_debate_adjudicators_column(self, debates, title="Adjudicators",
            show_splits=False, highlight_adj=None, for_admin=False):
        da_data = []

        def construct_text(adjs_data):
            adjs_list = []
            for a in adjs_data:
                adj_str = '<span class="d-inline">' + escape_if_unsafe(a['adj'].get_public_name(self.tournament))
                symbol = self.ADJ_SYMBOLS.get(a['position'])
                if symbol:
                    adj_str += "<i class='adj-symbol'>%s</i>" % symbol
                if a.get('split', False):
                    adj_str += " <span class='text-danger'>💢</span>"
                if a['adj'] == highlight_adj:
                    adj_str = "<strong>" + adj_str + "</strong>"
                adj_str += '</span>'
                adjs_list.append(adj_str)
            return ("<div class='clearfix pt-1 pb-1 d-block d-md-none'> "
                    "</div><span class='d-none d-md-inline'>, </span>").join(adjs_list)

        def construct_popover(adjs_data):
            popover_data = []
            for a in adjs_data:
                descriptors = []
                if a['position'] != AdjudicatorAllocation.POSITION_ONLY:
                    descriptors.append(self.ADJ_POSITION_NAMES[a['position']])
                if (for_admin or self.tournament.pref('show_adjudicator_institutions')) and \
                        a['adj'].institution is not None:
                    descriptors.append(escape(a['adj'].institution.code))
                if a.get('split', False):
                    descriptors.append("<span class='text-danger'>" + _("in minority") + "</span>")
                text = escape_if_unsafe(a['adj'].get_public_name(self.tournament))

                descriptors = " (%s)" % (", ".join(descriptors)) if descriptors else ""

                if self._show_record_links:
                    popover_data.append(self._adjudicator_record_link(a['adj'], suffix=descriptors))
                else:
                    popover_data.append({'text': text + "" + descriptors})

            return popover_data

        for debate in debates:
            adjs_data = []
            # The purpose of the second condition is to short-circuit debate.confirmed_ballot
            if show_splits and self.tournament.ballots_per_debate(debate.round.stage) == 'per-adj' \
                    and debate.confirmed_ballot \
                    and debate.confirmed_ballot.result.is_voting \
                    and debate.confirmed_ballot.result.is_valid() \
                    and (self.admin or self.tournament.pref('show_splitting_adjudicators')):
                for adj, position, split in debate.confirmed_ballot.result.adjudicators_with_splits():
                    adjs_data.append({'adj': adj, 'position': position, 'split': bool(split)})
            else:
                for adj, position in debate.adjudicators.with_positions():
                    adjs_data.append({'adj': adj, 'position': position})

            if not debate.adjudicators.has_chair and debate.adjudicators.is_panel:
                adjs_data[0]['type'] = 'O'

            da_data.append({
                'class': 'adjudicator-name',
                'text': construct_text(adjs_data),
                'popover': {
                    'title': _("Debate Adjudicators"),
                    'content' : construct_popover(adjs_data),
                },
            })

        self.add_column({'key': 'adjudicators', 'title': _(title)}, da_data)

    def add_debate_motion_column(self, debates):
        """Shows the motions associated with the debates.
        The mechanism depends on whether the 'enable_motions' preferences is enabled:
        if it is, then the motion is attached to the debate's confirmed ballot; if
        not, then it's just attached to the round."""
        motions = []
        for debate in debates:
            released = debate.round.motions_released or debate.round.tournament.pref('all_results_released')
            if self.tournament.pref('enable_motions') or released:
                motions.append(getattr(debate.confirmed_ballot, 'motion', None))
            else:
                motions.append(None)
        self.add_motion_column(motions)

    def add_motion_column(self, motions):
        motion_data = [{
            'text': escape(motion.reference) if motion.reference else _('??'),
            'popover': {'content' : [{'text': escape(motion.text)}]},
        } if motion else self.BLANK_TEXT for motion in motions]
        self.add_column({'key': "motion", 'title': _("Motion")}, motion_data)

    def add_team_columns(self, teams, show_break_categories=False, show_emoji=True, key=None):
        """If `show_break_categories` is True, each team must be annotated with
        a `break_categories_nongeneral` attribute, which typically looks like this:
            Prefetch('break_categories', queryset=BreakCategory.objects.filter(is_general=False),
                to_attr='break_categories_nongeneral')
        """

        team_data = [self._team_cell(team, show_emoji=show_emoji)
                     if not (getattr(team, 'anonymise', False) and not self.admin)
                     else self.BLANK_TEXT for team in teams]
        if key:
            header = {'key': key, 'text': key}
        else:
            header = {'key': 'team', 'tooltip': _("Team"), 'icon': 'users'}
        self.add_column(header, team_data)

        if show_break_categories and self.tournament.breakcategory_set.filter(is_general=False).exists():
            self.add_column(
                {'key': 'categories', 'icon': 'user-check', 'tooltip': _("Categories")},
                [", ".join(escape(bc.name) for bc in getattr(team, 'break_categories_nongeneral', []))
                    for team in teams],
            )

        if self.tournament.pref('show_team_institutions'):
            self.add_column({
                'key': "institution",
                'icon': 'home',
                'tooltip': _("Institution"),
            }, [
                escape(team.institution.code)
                if not getattr(team, 'anonymise', False) and team.institution is not None
                else self.BLANK_TEXT for team in teams
            ])

    def add_speaker_columns(self, speakers, categories=True):
        speaker_data = []
        for speaker in speakers:
            anonymous = getattr(speaker, 'anonymise', False) or speaker.anonymous
            if anonymous and not (self.admin and has_permission(self.user, Permission.VIEW_ANONYMOUS, self.tournament)):
                speaker_data.append(self.REDACTED_CELL)
            else:
                cell = {
                    'text': escape_if_unsafe(speaker.get_public_name(self.tournament)),
                    'class': 'no-wrap' if len(speaker.get_public_name(self.tournament)) < 20 else '',
                }
                if anonymous:
                    cell['class'] += ' admin-redacted'
                speaker_data.append(cell)

        self.add_column({'key': 'name', 'tooltip': _("Name"), 'icon': 'user'}, speaker_data)

        if categories:
            speakercategory_set = self.tournament.speakercategory_set
            if not self.admin:
                speakercategory_set = speakercategory_set.filter(public=True)

            if speakercategory_set.exists():
                categories_data = []
                for speaker in speakers:
                    category_strs = []
                    for cat in speaker.categories.all():
                        if cat.public:
                            category_strs.append(escape(cat.name))
                        elif self.admin:
                            category_strs.append("<em>" + escape(cat.name) + "</em>")
                    categories_data.append(", ".join(category_strs))

                self.add_column({
                    'key': "category",
                    'title': _("Category"),
                    'icon': 'user-check', # Not ideal but full name blows out tables
                    'tooltip': _("Categories"),
                }, categories_data)

    def add_debate_venue_columns(self, debates, with_times=True, for_admin=False):

        def construct_venue_cell(venue):
            if not venue:
                return {'text': ''}

            cell = {'text': escape(venue.display_name), 'class': 'venue-name', 'link': escape(venue.url)}

            categories = venue.venuecategory_set.all()
            if not for_admin:
                # filter in Python, not SQL, because venuecategory_set should have been prefetched
                categories = [c for c in categories if c.display_in_public_tooltip]

            if len(categories) == 0:
                return cell

            descriptions = [escape(category.description.strip()) for category in categories]
            descriptions = ["<strong>" + description + "</strong>"
                    for description in descriptions if len(description) > 0]

            if len(descriptions) > 0:
                if len(descriptions) == 1:
                    categories_sentence = _("This room %(predicate)s.") % {'predicate': descriptions[0]}
                else:
                    categories_sentence = _("This room %(predicates)s, and %(last_predicate)s.") % {
                        'predicates': ", ".join(descriptions[:-1]),
                        'last_predicate': descriptions[-1]}

                cell['popover'] = {
                    'title': escape(venue.display_name),
                    'content': [{'text': categories_sentence}]}

            return cell

        venue_data = [construct_venue_cell(d.venue) for d in debates]

        venue_header = {
            'key': 'venue',
            'icon': 'map-pin',
            'tooltip': _("Room"),
        }
        self.add_column(venue_header, venue_data)

    def add_draw_conflicts_columns(self, debates, venue_conflicts, adjudicator_conflicts):

        conflicts_by_debate = []
        for debate in debates:
            # conflicts is a list of (level, message) tuples
            conflicts = [("secondary", _draw_flags_dict.get(flag, flag)) for flag in debate.flags]
            if not debate.is_bye:
                conflicts += [("secondary", "%(team)s: %(flag)s" % {
                            'team': self._team_short_name(dt.team),
                            'flag': _draw_flags_dict.get(flag, flag),
                        }) for dt in debate.debateteams for flag in dt.flags]

            if self.tournament.pref('avoid_team_history'):
                history = debate.history
                if history > 0:
                    conflicts.append(("warning", ngettext("Teams have met once",
                            "Teams have met %(count)d times", history) % {'count': history}))

            if self.tournament.pref('avoid_same_institution'):
                institutions = [t.institution_id for t in debate.teams if t.institution_id is not None]
                if len(set(institutions)) != len(institutions):
                    conflicts.append(("warning", _("Teams are from the same institution")))

            conflicts.extend(adjudicator_conflicts[debate])  # Escaped in adjallocation.utils
            conflicts.extend(venue_conflicts[debate])  # Escaped in venues.utils
            conflicts_by_debate.append(conflicts)

        conflicts_header = {'title': _("Conflicts/Flags"), 'key': 'conflags'}
        conflicts_data = [{
            'text': "".join(["<div class=\"text-{0}\">{1}</div>".format(*conflict) for conflict in debate_conflicts]),
            'class': 'small',
        } for debate_conflicts in conflicts_by_debate]
        self.add_column(conflicts_header, conflicts_data)

    def _standings_headers(self, info_list):
        headers = []
        for info in info_list:
            header = {'key': info['abbr'],
                      'tooltip': force_str(info['name']).capitalize()}
            if info['icon']:
                header['icon'] = info['icon']
            else:
                header['title'] = force_str(info['abbr'])

            headers.append(header)
        return headers

    def add_ranking_columns(self, standings):
        headers = self._standings_headers(standings.rankings_info())
        data = []
        for standing in standings:
            data.append([{
                'text': rankingformat(ranking),
                'sort': ranking[0] or 99999,
            } for ranking in standing.iterrankings()])
        self.add_columns(headers, data)

    def add_metric_columns(self, standings, integer_score_columns=None):
        """`integer_score_columns`, if given, indicates which metrics to cast to
        an int if the metric's value is an integer. For example, if the
        tournament preferences are such that the total speaker score should
        always be an integer, a list containing the string 'total' or
        'speaks_sum' should be passed in via this argument."""
        if integer_score_columns is None:
            integer_score_columns = []

        headers = self._standings_headers(standings.metrics_info())
        data = []
        for standing in standings:
            row = []
            for key, metric in zip(standings.metric_keys, standing.itermetrics()):
                if metric is None:
                    row.append({'text': '—', 'sort': 0})
                    continue

                if key in integer_score_columns and hasattr(metric, 'is_integer') and metric.is_integer():
                    metric = int(metric)
                try:
                    sort = float(metric)
                except (TypeError, ValueError):
                    sort = 99999
                row.append({'text': metricformat(metric), 'sort': sort})
            data.append(row)
        self.add_columns(headers, data)

    def add_speaker_debate_ballot_link_column(self, debates):
        ballot_links_header = {'key': "ballot", 'icon': 'search', 'tooltip': _("The confirmed ballot")}
        ballot_links_data = []

        for debate in debates:
            if not debate.confirmed_ballot:
                ballot_links_data.append(_("No ballot"))
            elif not debate.confirmed_ballot.result.uses_speakers:
                ballot_links_data.append(_("No scores"))
            else:
                ballot_links_data.append({
                    'text': _("View Ballot"),
                    'link': reverse_round(
                        'speaker-results-privateurl-scoresheet', debate.round, kwargs={'url_key': self.private_url_key}),
                })
        self.add_column(ballot_links_header, ballot_links_data)

    def add_debate_ballot_link_column(self, debates, show_ballot=False):
        ballot_links_header = {'key': "ballot", 'icon': 'search',
                               'tooltip': _("The ballot you submitted")}
        no_ballot = _("No Ballot")

        if self.admin:
            ballot_links_data = [{
                'text': no_ballot if debate.is_bye else _("View/Edit Ballot"),
                'link': None if debate.is_bye else reverse_tournament('old-results-ballotset-edit', self.tournament, kwargs={'pk': debate.confirmed_ballot.id}),
            } if debate.confirmed_ballot else "" for debate in debates]
            self.add_column(ballot_links_header, ballot_links_data)

        elif self.private_url:
            debateqs = Debate.objects.filter(pk__in=[d.pk for d in debates]).select_related('round').annotate(
                has_ballot=Exists(BallotSubmission.objects.filter(debate_id=OuterRef('id')).exclude(discarded=True)),
            ).prefetch_related(
                Prefetch('ballotsubmission_set', queryset=BallotSubmission.objects.exclude(discarded=True), to_attr='nondiscard_ballots'),
            ).all()
            annotated_debates = {d.pk: d for d in debateqs}
            ballot_links_data = []
            for o_debate in debates:
                debate = annotated_debates[o_debate.pk]
                if not debate.has_ballot:
                    ballot_links_data.append(no_ballot)
                elif not get_result_class(debate.nondiscard_ballots[0], debate.round, self.tournament).uses_speakers:
                    ballot_links_data.append(_("No scores"))
                else:
                    ballot_links_data.append({
                        'text': no_ballot if debate.is_bye else _("View Ballot"),
                        'link': None if debate.is_bye else reverse_round(
                            'results-privateurl-scoresheet-view', debate.round, kwargs={'url_key': self.private_url_key}),
                    })
            self.add_column(ballot_links_header, ballot_links_data)

        elif self.tournament.pref('ballots_released'):
            ballot_links_data = []
            for debate in debates:
                if self.tournament.pref('teams_in_debate') == 4 and debate.round.is_break_round:
                    ballot_links_data.append("")
                elif debate.is_bye:
                    ballot_links_data.append(no_ballot)
                else:
                    ballot_links_data.append({
                        'text': _("View Ballot"),
                        'link': reverse_tournament('results-public-scoresheet-view', self.tournament,
                            kwargs={'pk': debate.id}),
                    })
            self.add_column(ballot_links_header, ballot_links_data)

    def add_debate_result_by_team_column(self, teamscores):
        results_data = [self._result_cell(ts) for ts in teamscores]
        header = {'key': 'result', 'tooltip': _("Result"), 'icon': 'thermometer'}
        self.add_column(header, results_data)

    def add_debate_side_by_team_column(self, teamscores, tournament=None):
        sides_data = []
        for ts in teamscores:
            if not ts.debate_team.debate.sides_confirmed:
                # Translators: "TBC" stands for "to be confirmed".
                side = _("TBC")
            side = ts.debate_team.get_side_name(tournament).title()

            if ts.debate_team.side == 'bye':
                side = {'text': f"<span class='text-info'>{side}</span>"}

            sides_data.append(side)

        header = {'key': 'side', 'title': _("Side")}
        self.add_column(header, sides_data)

    def add_team_results_columns(self, teams, rounds):
        """Takes an iterable of Teams, assumes their round_results match rounds"""
        for round_seq, round in enumerate(rounds):
            results = [self._result_cell(
                t.round_results[round_seq]) for t in teams]
            # Should the key be the round abbreviation (like for standings_results_columns)?
            header = {'key': 'r%d' % round_seq, 'title': escape(round.abbreviation)}
            self.add_column(header, results)

    def add_debate_results_columns(self, debates, iron=False, n_cols=None):
        all_sides_confirmed = all(debate.sides_confirmed for debate in debates)  # should already be fetched
        n_cols = n_cols or len(self.tournament.sides)
        side_abbrs = {side: get_side_name(self.tournament, side, 'abbr') for side in range(n_cols)}

        results_data = []
        for debate in debates:
            row = []

            if debate.is_bye:
                cell = self._team_cell(debate.get_team('bye'), show_emoji=False, subtext=_("Bye"))
                cell['popover']['content'].append({'text': "<span class='%s'>%s</span>"
                        % ('text-info', _("Team was given a bye this round"))})
                row.append(cell)
                row += [{'text': self.BLANK_TEXT} for i in range(n_cols - 1)]
                results_data.append(row)
                continue

            for side in range(n_cols):
                if side >= len(debate.teams):
                    row += [{'text': self.BLANK_TEXT} for i in range(n_cols - side)]
                    break

                debateteam = debate.get_dt(side)
                team = debate.get_team(side)

                subtext = None if (all_sides_confirmed or not debate.sides_confirmed) else side_abbrs[side]
                cell = self._team_cell(team, show_emoji=False, subtext=subtext)

                if self.tournament.pref('teams_in_debate') == 2:
                    cell = self._result_cell_class_two(debateteam.win, cell)
                elif debate.round.is_break_round:
                    cell = self._result_cell_class_four_elim(debateteam.win, cell)
                else:
                    cell = self._result_cell_class_four(debateteam.points, cell, len(debate.teams))

                if iron and (debateteam.iron > 0 or debateteam.iron_prev > 0):
                    cell['text'] = "🗣️" + cell['text']

                    popover_text = []
                    if debateteam.iron > 0 and debateteam.iron_prev > 0:
                        popover_text = _("Team iron-personed this round and the last.")
                        warning_level = "text-info"
                    elif debateteam.iron > 0:
                        popover_text = _("Team iron-personed this round.")
                        warning_level = "text-info"
                    else:
                        popover_text = _("Team iron-personed last round.")
                        warning_level = "text-warning"

                    cell['class'] = "%s strong" % warning_level
                    cell['popover']['content'].append({'text': "<span class='%s'>%s</span>"
                        % (warning_level, popover_text)})

                row.append(cell)
            results_data.append(row)

        if all_sides_confirmed:
            results_header = [{
                'title': get_side_name(self.tournament, side, 'abbr'),
                'key': get_side_name(self.tournament, side, 'abbr'),
            } for side in range(n_cols)]
        else:
            results_header = [{
                'title': _("Team %(num)d") % {'num': i},
                'key': _("Team %(num)d") % {'num': i},
            } for i in range(1, len(side_abbrs)+1)]

        self.add_columns(results_header, results_data)

    def add_debate_postponement_column(self, debates):
        col_data = [render_to_string('debate_postponement_form.html', {'debate': d}) for d in debates]
        header = {'key': 'postpone', 'title': _("Postpone")}
        self.add_column(header, col_data)

    def add_standings_results_columns(self, standings, rounds, show_ballots):

        for round_seq, round in enumerate(rounds):
            header = {'title': escape(round.abbreviation), 'key': escape(round.abbreviation)}
            results = [self._result_cell(
                s.round_results[round_seq],
                compress=True,
                show_score=True,
                show_ballots=show_ballots,
            ) for s in standings]
            self.add_column(header, results)
