from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.consumers import ConsumerLoginRequiredMixin, TournamentConsumer

from .models import ActionLogEntry


class ActionLogEntryConsumer(ConsumerLoginRequiredMixin, TournamentConsumer):
    group_base_string = 'actionlog'

    def get_tournament_id_from_content(self, content):
        return content.tournament.id

    def make_payload(self, content):
        return content.serialize


# Send out updates upon new action log entries
@receiver(post_save, sender=ActionLogEntry)
def consumer(sender, instance, created, **kwargs):
    if created:
        ActionLogEntryConsumer.group_send(instance)
