from utils.consumers import TournamentConsumerMixin, WSLoginRequiredMixin


class ActionLogEntryConsumer(TournamentConsumerMixin, WSLoginRequiredMixin):

    group_prefix = 'actionlogs'
