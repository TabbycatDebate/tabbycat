from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.consumers import TournamentConsumer, WSLoginRequiredMixin

from .models import Event


class CheckInEventConsumer(TournamentConsumer, WSLoginRequiredMixin):

    group_prefix = 'checkins'


# Send out all the current events when a new check=in event is made
@receiver(post_save, sender=Event)
def checkin_event_notify_consumer(sender, instance, created, **kwargs):
    if created:
        slug = instance.tournament.slug
        group_name = CheckInEventConsumer.group_prefix + "_" + slug
        AsyncToSync(get_channel_layer().group_send)(group_name, {
            "type": "broadcast",
            "data": instance.serialize()
        })
