from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from results.models import BallotSubmission
from results.utils import graphable_debate_statuses

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
        print(instance.id, 'serialised ballots for results')
        return instance.serialize_like_actionlog


class DebateStatusBinding(WebsocketBinding):

    model = BallotSubmission
    stream = "status"
    fields = ["__all__"]

    @classmethod
    def group_names(cls, instance):
        return ["debate-status-updates"]

    def has_permission(self, user, action, pk):
        return True

    # Override default method
    def serialize_data(self, instance):
        ballots = BallotSubmission.objects.filter(discarded=False)
        cr = ballots[0].debate.round.tournament.current_round
        ballots = ballots.filter(debate__round=cr)
        stats = graphable_debate_statuses(ballots, cr)
        print(instance.id, 'serialised ballots for graph')
        return stats


class TournamentOverviewDemultiplexer(WebsocketDemultiplexer):

    http_user_and_session = True # Require user login and user session

    consumers = {
        # These must match the streams in WebsocketBinding (I think)
        "actionlog": ActionLogEntryBinding.consumer,
        "ballot": BallotSubmissionBinding.consumer,
        "status": DebateStatusBinding.consumer
    }

    def connection_groups(self):
        # These must match group_names in the WebsocketBindings (I think)
        return ["actionlog-updates", "ballot-updates", "debate-status-updates"]
