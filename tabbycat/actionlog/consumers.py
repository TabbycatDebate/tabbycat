from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.consumers import TournamentConsumer, WSLoginRequiredMixin

from .models import ActionLogEntry


class ActionLogEntryConsumer(TournamentConsumer, WSLoginRequiredMixin):

    group_prefix = 'actionlog'


# Send out updates upon new action log entries
@receiver(post_save, sender=ActionLogEntry)
def consumer(sender, instance, created, **kwargs):
    if created:
        slug = instance.tournament.slug
        group_name = ActionLogEntryConsumer.group_prefix + "_" + slug
        AsyncToSync(get_channel_layer().group_send)(group_name, {
            "type": "broadcast",
            "data": instance.serialize,
        })
