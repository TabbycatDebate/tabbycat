from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from results.models import BallotSubmission

from .models import ActionLogEntry


class ActionLogEntryBinding(WebsocketBinding):

    model = ActionLogEntry
    stream = "actionlog"
    fields = ["__all__"]

    @classmethod
    def group_names(cls, instance):
        return ["actionlog-updates"]

    def has_permission(self, user, action, pk):
        return True

    # Override default method
    def serialize_data(self, instance):
        return instance.serialize


class BallotSubmissionBinding(WebsocketBinding):

    model = BallotSubmission
    stream = "ballot"
    fields = ["__all__"]

    @classmethod
    def group_names(cls, instance):
        return ["ballot-updates"]

    def has_permission(self, user, action, pk):
        return True

    # Override default method
    def serialize_data(self, instance):
        return instance.serialize_like_actionlog


class TournamentOverviewDemultiplexer(WebsocketDemultiplexer):

    consumers = {
        # These must match the streams in WebsocketBinding (I think)
        "actionlog": ActionLogEntryBinding.consumer,
        "ballot": BallotSubmissionBinding.consumer,
    }

    def connection_groups(self):
        # These must match group_names in the WebsocketBindings (I think)
        return ["actionlog-updates", "ballot-updates"]
