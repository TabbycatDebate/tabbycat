from utils.consumers import TournamentConsumer, WSLoginRequiredMixin

from results.models import BallotSubmission
from results.utils import graphable_debate_statuses


class BallotResultConsumer(TournamentConsumer, WSLoginRequiredMixin):
    group_prefix = 'ballot_results'


class BallotStatusConsumer(TournamentConsumer, WSLoginRequiredMixin):
    group_prefix = 'ballot_statuses'

    @classmethod
    def get_data(cls, debate_round):
        ballots = BallotSubmission.objects.filter(debate__round=debate_round,
                                                  discarded=False)
        return graphable_debate_statuses(ballots, debate_round)
