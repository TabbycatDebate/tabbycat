from utils.consumers import DebateOrPanelConsumer

from adjallocation.models import DebateAdjudicator

from .models import Debate


class DebateEditConsumer(DebateOrPanelConsumer):
    """ Adapts the generic methods for updating adjudicators to update debate
    adjudicators specifically (instead of preformed panel adjudicators) """

    group_prefix = 'debates'

    def delete_adjudicators(self, debate, adj_ids):
        return debate.debateadjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, debate, adj_id, adj_type):
        return DebateAdjudicator.objects.update_or_create(
            debate=debate,
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def get_objects(self, ids):
        return Debate.objects.filter(id__in=ids)
