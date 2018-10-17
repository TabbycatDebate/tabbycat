from utils.consumers import TournamentConsumerMixin, WSLoginRequiredMixin


class BallotResultConsumer(TournamentConsumerMixin, WSLoginRequiredMixin):
    group_prefix = 'ballot_results'


class BallotStatusConsumer(TournamentConsumerMixin, WSLoginRequiredMixin):
    group_prefix = 'ballot_statuses'
