from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from results.models import BallotSubmission
from results.utils import graphable_debate_statuses

from .models import ActionLogEntry


class ActionLogEntryBinding(WebsocketBinding):

    model = ActionLogEntry
    stream = "actionlog"
    fields = ["__all__"]
    # We set the group_format dynamically to include the tournament ID
    # So that the group becomes a per-tournament subscription to prevent mixed
    # updates from different tournaments
    group_format = 'actionlog-updates-{tournament_id}'

    @classmethod
    def group_names(cls, instance):
        return [cls.group_format.format(tournament_id=instance.tournament_id)]

    # Override default method
    def serialize_data(self, instance):
        return instance.serialize


class BallotSubmissionBinding(WebsocketBinding):

    model = BallotSubmission
    stream = "ballot"
    fields = ["__all__"]
    group_format = 'ballot-updates-{tournament_id}'

    @classmethod
    def group_names(cls, instance):
        return [cls.group_format.format(tournament_id=instance.tournament_id)]

    # Override default method'
    def serialize_data(self, instance):
        return instance.serialize_like_actionlog


class DebateStatusBinding(WebsocketBinding):

    model = BallotSubmission
    stream = "status"
    fields = ["__all__"]
    group_format = 'debate-status-updates-{tournament_id}'

    @classmethod
    def group_names(cls, instance):
        return [cls.group_format.format(tournament_id=instance.tournament_id)]

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

    def connection_groups(self, *args, **kwargs):
        # These must match group_names in the WebsocketBindings (I think)
        print('test', kwargs['tournament_id'])
        tournament_id = kwargs['tournament_id']
        return [
            "actionlog-updates" + "-" + tournament_id,
            "ballot-updates" + "-" + tournament_id,
            "debate-status-updates" + "-" + tournament_id
        ]
