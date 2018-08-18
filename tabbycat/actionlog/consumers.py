from utils.consumers import TournamentConsumer, WSLoginRequiredMixin


class ActionLogEntryConsumer(TournamentConsumer, WSLoginRequiredMixin):

    group_prefix = 'actionlogs'
