from channels.generic.websocket import JsonWebsocketConsumer

from tournaments.mixins import TournamentWebsocketMixin
from utils.mixins import LoginRequiredWebsocketMixin


class ActionLogEntryConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'actionlogs'
