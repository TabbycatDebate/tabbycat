from smtplib import SMTPException

from django.contrib import messages
from django.utils.translation import gettext as _

from notifications.utils import BallotEmailGenerator
from utils.misc import get_ip_address

from .models import Submission
from .result import DebateResult


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


class BallotEmailWithStatusMixin:
    def send_email_receipts(self):
        try:
            BallotEmailGenerator.run(DebateResult(self.ballotsub).as_dicts(), self.debate)
        except SMTPException:
            messages.error(self.request, _("There was a problem sending ballot receipts to adjudicators."))
            return False
        except ConnectionError:
            messages.error(self.request, _("There was a problem connecting to the e-mail server when trying to send ballot receipts to adjudicators."))
            return False
        else:
            return True
