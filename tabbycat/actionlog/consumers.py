from channels.generic.websocket import JsonWebsocketConsumer

from utils.consumers import LoginRequiredWebsocketMixin, TournamentWebsocketMixin


class ActionLogEntryConsumer(LoginRequiredWebsocketMixin, TournamentWebsocketMixin, JsonWebsocketConsumer):
    group_prefix = 'actionlogs'
