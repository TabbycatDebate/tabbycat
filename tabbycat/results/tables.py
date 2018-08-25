from django.utils.translation import gettext as _

from draw.models import Debate
from utils.misc import reverse_tournament
from utils.tables import TabbycatTableBuilder

from .utils import get_status_meta


class ResultsTableBuilder(TabbycatTableBuilder):
    """Painfully construct the edit links; this is the only case where
    a cell has multiple links; hence the creating HTML directly"""

    def add_ballot_check_in_columns(self, debates, key):

        status_header = {
            'key': key,
            'tooltip': _("Whether this debate's ballot has been checked-in"),
            'icon': "compass",
        }
        status_cells = []
        for debate in debates:
            cell = {
                'icon': 'check' if debate.checked_in else 'x',
                'class': 'text-primary' if debate.checked_in else 'text-muted',
                'sort': 1 if debate.checked_in else 0,
                'tooltip': debate.checked_tooltip,
                'check': 'checked' if debate.checked_in else 'missing', # Hook for vue
                'id': debate.id,
                'identifier': debate.barcode if debate.barcode else None,
            }
            status_cells.append(cell)
        self.add_column(status_header, status_cells)

    def add_ballot_status_columns(self, debates, key):

        status_header = {
            'key': key,
            'tooltip': _("Status of this debate's ballot"),
            'icon': "crosshair",
        }
        status_cells = []
        for debate in debates:
            meta = get_status_meta(debate)
            cell = {
                'icon': meta[0],
                'class': meta[1],
                'sort': meta[2],
                'tooltip': meta[3],
                'status': debate.result_status, # Hook for vue
                'id': debate.id
            }
            status_cells.append(cell)
        self.add_column(status_header, status_cells)

    def get_ballot_cells(self, debate, tournament, user):
        # These are prefetched, so sort using Python rather than generating an SQL query
        ballotsubmissions = sorted(debate.ballotsubmission_set.all(), key=lambda x: x.version)
        if user.is_superuser:
            link = 'results-ballotset-new'
        else:
            link = 'results-assistant-ballotset-new'

        return {
            'component': 'ballots-cell',
            'ballots': [b.serialize(tournament) for b in ballotsubmissions],
            'admin': True if user.is_superuser else False,
            'new_ballot': reverse_tournament(link, self.tournament,
                                             kwargs={'debate_id': debate.id})
        }

    def add_ballot_entry_columns(self, debates, user):

        entry_header = {'key': 'EB', 'icon': "plus-circle"}
        entry_cells = [self.get_ballot_cells(d, self.tournament, user) for d in debates]
        self.add_column(entry_header, entry_cells)

        if self.tournament.pref('enable_postponements'):
            postpones_header = {'title': _("Postpone"), 'key': "postpone"}
            postpones_cells = []
            for debate in debates:
                if debate.result_status == Debate.STATUS_POSTPONED:
                    text = '<a href="#" class="unpostpone-link" debate-id="{:d}">' + _("Unpostpone") + '</a>'
                else:
                    text = '<a href="#" class="postpone-link" debate-id="{:d}">' + _("Postpone") + '</a>'
                postpones_cells.append(text.format(debate.id))
            self.add_column(postpones_header, postpones_cells)
