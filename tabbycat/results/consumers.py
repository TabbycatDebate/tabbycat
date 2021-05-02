from channels.generic.websocket import JsonWebsocketConsumer

from tournaments.mixins import TournamentWebsocketMixin
from utils.mixins import LoginRequiredWebsocketMixin


class BallotResultConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'ballot_results'


class BallotStatusConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'ballot_statuses'
