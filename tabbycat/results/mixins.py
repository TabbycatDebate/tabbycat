from utils.misc import get_ip_address

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
