from utils.consumers import ConsumerLoginRequiredMixin, TournamentConsumer


class BallotSubmissionConsumer(ConsumerLoginRequiredMixin, TournamentConsumer):
    group_base_string = 'ballot'

    def get_tournament_id_from_content(self, content):
        return content.debate.round.tournament.id

    def make_payload(self, content):
        return content.serialize_like_actionlog
