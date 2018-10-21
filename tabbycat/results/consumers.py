from channels.generic.websocket import JsonWebsocketConsumer

from utils.consumers import LoginRequiredWebsocketMixin, TournamentWebsocketMixin


class BallotResultConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'ballot_results'


class BallotStatusConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'ballot_statuses'
