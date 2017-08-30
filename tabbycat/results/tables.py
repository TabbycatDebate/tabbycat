from draw.models import Debate
from participants.models import Team
from utils.misc import reverse_tournament
from utils.tables import TabbycatTableBuilder


class ResultsTableBuilder(TabbycatTableBuilder):
    """Painfully construct the edit links; this is the only case where
    a cell has multiple links; hence the creating HTML directly"""

    def get_status_meta(self, debate):
        if any(team.type == Team.TYPE_BYE for team in debate.teams):
            return "fast-forward", "", 5, "Bye Debate"
        elif debate.result_status == Debate.STATUS_NONE and not debate.ballot_in:
            return "x", "text-danger", 0, "No Ballot"
        elif debate.result_status == Debate.STATUS_NONE and debate.ballot_in:
            return "inbox", "text-warning", 1, "Ballot is In"
        elif debate.result_status == Debate.STATUS_DRAFT:
            return "sliders", "text-info", 2, "Ballot is Unconfirmed"
        elif debate.result_status == Debate.STATUS_CONFIRMED:
            return "check", "text-success", 3, "Ballot is Confirmed"
        elif debate.result_status == Debate.STATUS_POSTPONED:
            return "pause", "", 4, "Debate was Postponed"
        else:
            raise ValueError('Debate has no discernable status')

    def add_ballot_status_columns(self, debates, key="Status"):

        status_header = {
            'key': key,
            'tooltip': "Status of this debate's ballot",
            'icon': "crosshair",
        }
        status_cell = [{
            'icon': self.get_status_meta(debate)[0],
            'class': self.get_status_meta(debate)[1],
            'sort': self.get_status_meta(debate)[2],
            'tooltip': self.get_status_meta(debate)[3]
        } for debate in debates]
        self.add_column(status_header, status_cell)

    def get_ballot_text(self, debate):
        ballotsubs_info = " "

        # These are prefetched, so sort using Python rather than generating an SQL query
        ballotsubmissions = sorted(debate.ballotsubmission_set.all(), key=lambda x: x.version)

        for ballotsub in ballotsubmissions:
            if not self.admin and ballotsub.discarded:
                continue

            link = reverse_tournament('results-ballotset-edit',
                                      self.tournament,
                                      kwargs={'pk': ballotsub.id})
            ballotsubs_info += "<a href=" + link + ">"

            if ballotsub.confirmed:
                edit_status = "Re-edit v" + str(ballotsub.version)
            elif self.admin:
                edit_status = "Edit v" + str(ballotsub.version)
            else:
                edit_status = "Review v" + str(ballotsub.version)

            if ballotsub.discarded:
                ballotsubs_info += "<strike class='text-muted'>" + edit_status + "</strike></a><small> discarded; "
            else:
                ballotsubs_info += edit_status + "</a><small>"

            if ballotsub.submitter_type == ballotsub.SUBMITTER_TABROOM:
                ballotsubs_info += " <em>entered by " + ballotsub.submitter.username + "</em>"
            elif ballotsub.submitter_type == ballotsub.SUBMITTER_PUBLIC:
                ballotsubs_info += " <em>a public submission by " + ballotsub.ip_address + "</em>"

            ballotsubs_info += "</small><br />"

        if all(x.discarded for x in ballotsubmissions):
            link = reverse_tournament('results-ballotset-new',
                                      self.tournament,
                                      kwargs={'debate_id': debate.id})
            ballotsubs_info += "<a href=" + link + ">Enter Ballot</a>"

        return ballotsubs_info

    def add_ballot_entry_columns(self, debates):

        entry_header = {'key': 'EB', 'icon': "plus-circle"}
        entry_cells = [{'text': self.get_ballot_text(d)} for d in debates]
        self.add_column(entry_header, entry_cells)

        if self.tournament.pref('enable_postponements'):
            postpones_header = {'key': 'Postpone'}
            postpones_cells = []
            for debate in debates:
                if debate.result_status == Debate.STATUS_POSTPONED:
                    text = '<a href="#" class="unpostpone-link" debate-id="{:d}">Unpostpone</a>'
                else:
                    text = '<a href="#" class="postpone-link" debate-id="{:d}">Postpone</a>'
                postpones_cells.append(text.format(debate.id))
            self.add_column(postpones_header, postpones_cells)
