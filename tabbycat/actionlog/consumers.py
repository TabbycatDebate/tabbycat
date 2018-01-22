from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.consumers import ConsumerLoginRequiredMixin, TournamentConsumer

from .models import ActionLogEntry


class ActionLogEntryConsumer(ConsumerLoginRequiredMixin, TournamentConsumer):
    group_base_string = 'actionlog'

    @staticmethod
    def get_tournament_id_from_content(actionlog):
        return actionlog.tournament.id

    @staticmethod
    def make_payload(actionlog):
        return actionlog.serialize


# Send out updates upon new action log entries
@receiver(post_save, sender=ActionLogEntry)
def consumer(sender, instance, created, **kwargs):
    if created:
        ActionLogEntryConsumer.group_send(instance)
