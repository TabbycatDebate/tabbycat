from utils.misc import get_ip_address, reverse_tournament

from .models import Submission


class TabroomSubmissionFieldsMixin:
    """Mixin that provides retrieval of appropriate fields for the Submission
    instance, used with forms that are submitted by tabroom officials. It is up
    to subclasses to use get_submitter_fields() appropriately."""

    def get_submitter_fields(self):
        return {
            'submitter': self.request.user,
            'submitter_type': Submission.SUBMITTER_TABROOM,
            'ip_address': get_ip_address(self.request)
        }


class PublicSubmissionFieldsMixin:
    """Mixin that provides retrieval of appropriate fields for the Submission
    instance, used with forms that are submitted from the public pages. It is up
    to subclasses to use get_submitter_fields() appropriately."""

    def get_submitter_fields(self):
        return {
            'submitter_type': Submission.SUBMITTER_PUBLIC,
            'ip_address': get_ip_address(self.request)
        }


class DebateResultCellsMixin:
    """Painfully construct the edit links; this is the only case where
    a cell has multiple links; hence the creating HTML directly"""

    def status_cells(self, debate, key="Status"):
        if debate.aff_team.type == 'B' or debate.neg_team.type == 'B':
            icon, sorting, tooltip = "glyphicon-fast-forward", 5, "Bye Debate"
        elif debate.result_status == debate.STATUS_NONE and not debate.ballot_in:
            icon, sorting, tooltip = "glyphicon-remove text-danger", 0, "No Ballot"
        elif debate.result_status == debate.STATUS_NONE and debate.ballot_in:
            icon, sorting, tooltip = "glyphicon-inbox text-warning", 1, "Ballot is In"
        elif debate.result_status == debate.STATUS_DRAFT:
            icon, sorting, tooltip = "glyphicon-adjust text-info", 2, "Ballot is Unconfirmed"
        elif debate.result_status == debate.STATUS_CONFIRMED:
            icon, sorting, tooltip = "glyphicon-ok text-success", 3, "Ballot is Confirmed"
        elif debate.result_status == debate.STATUS_POSTPONED:
            icon, sorting, tooltip = "glyphicon-pause", 4, "Debate was Postponed"
        else:
            raise ValueError('Debate has no discernable status')

        result_header = {
            'key': key,
            'tooltip': "Status of this debate's ballot",
            'icon': "glyphicon-th-list",
        }
        result_cell = {
            'icon': icon,
            'sort': sorting,
            'tooltip': tooltip
        }
        result_info = [{'head': result_header, 'cell': result_cell}]
        return result_info

    def ballot_entry_cells(self, d, t):

        ballotsets_info = " "
        for ballotset in d.ballotsubmission_set_by_version:
            link = reverse_tournament('edit_ballotset', t, kwargs={'ballotsub_id': ballotset.id})
            ballotsets_info = "<a href=" + link + ">"

            if ballotset.confirmed:
                edit_status = "Re-edit v" + str(ballotset.version)
            else:
                edit_status = "Edit v" + str(ballotset.version)

            if ballotset.discarded:
                ballotsets_info += "<strike class='text-muted'>" + edit_status + "</strike></a><small> discarded; "
            else:
                ballotsets_info += edit_status + "</a><small> "

            if ballotset.submitter_type == ballotset.SUBMITTER_TABROOM:
                ballotsets_info += " <em>entered by " + ballotset.submitter.username + "</em></small><br>"
            elif ballotset.submitter_type == ballotset.SUBMITTER_PUBLIC:
                ballotsets_info += " <em>a public submission by " + ballotset.ip_address + "</em></small><br>"

        if not d.ballotsubmission_set_by_version_except_discarded:
            link = reverse_tournament('new_ballotset', t, kwargs={'debate_id': d.id})
            ballotsets_info += "<a href=" + link + ">Enter New</a>"

        ballot_cells = [{'head': {'key':'enter ballots'}, 'cell': {'text': ballotsets_info}}]

        if t.pref('enable_postponements'):
            pcell = {'link': reverse_tournament('toggle_postponed', t, kwargs={'debate_id': d.id})}
            if d.result_status == d.STATUS_POSTPONED:
                pcell['text'] = 'Un-Postpone'
            else:
                pcell['text'] = 'Postpone'

            ballot_cells.append({'head': 'postpone'}, {'cell': pcell})

        return ballot_cells
