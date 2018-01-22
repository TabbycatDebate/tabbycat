from utils.consumers import ConsumerLoginRequiredMixin, TournamentConsumer

from results.models import BallotSubmission
from results.utils import graphable_debate_statuses


class BallotResultConsumer(ConsumerLoginRequiredMixin, TournamentConsumer):
    group_base_string = 'ballot-results'

    @staticmethod
    def get_tournament_id_from_content(ballotsub):
        return ballotsub.debate.round.tournament.id

    @staticmethod
    def make_payload(ballotsub):
        return ballotsub.serialize_like_actionlog


class BallotStatusConsumer(ConsumerLoginRequiredMixin, TournamentConsumer):
    group_base_string = 'ballot-statuses'

    @staticmethod
    def get_tournament_id_from_content(current_round):
        return current_round.tournament.id

    @staticmethod
    def make_payload(current_round):
        ballots = BallotSubmission.objects.filter(debate__round=current_round,
                                                  discarded=False)
        return graphable_debate_statuses(ballots, current_round)
