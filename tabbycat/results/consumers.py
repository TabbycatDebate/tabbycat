from utils.consumers import TournamentConsumer, WSLoginRequiredMixin


class BallotResultConsumer(TournamentConsumer, WSLoginRequiredMixin):
    group_prefix = 'ballot_results'


class BallotStatusConsumer(TournamentConsumer, WSLoginRequiredMixin):
    group_prefix = 'ballot_statuses'
