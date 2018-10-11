from utils.consumers import DebateOrPanelConsumer

from .models import PreformedPanel, PreformedPanelAdjudicator


class PanelEditConsumer(DebateOrPanelConsumer):
    """ Adapts the generic methods for updating adjudicators to update preformed
    panel adjudicators specifically (instead of debate adjudicators) """

    group_prefix = 'panels'

    def delete_adjudicators(self, panel, adj_ids):
        return panel.preformedpaneladjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, panel, adj_id, adj_type):
        return PreformedPanelAdjudicator.objects.update_or_create(
            panel=panel,
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def get_objects(self, ids):
        return PreformedPanel.objects.filter(id__in=ids)
