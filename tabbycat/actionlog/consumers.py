from .models import ActionLogEntry

from django.db.models.signals import post_save
from django.dispatch import receiver

from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer


class ActionLogEntryConsumer(JsonWebsocketConsumer):
    http_user = True
    group_base_string = 'actionlog' # Serves as group prefix and pseudo-stream

    def connection_groups(self, **kwargs):
        return [self.group_string(kwargs["tournament_id"])]

    def connect(self, message, **kwargs):
        # Unauthenticated users come in as AnonymousUser; need to reject
        if not message.user.is_staff:
            return

        # Add the user to the tournament specific group; otherwise reject connection
        if kwargs['tournament_id']:
            Group(self.group_string(kwargs['tournament_id'])).add(message.reply_channel)
        else:
            message.reply_channel.send({"close": True})

    def disconnect(self, message, **kwargs):
        Group(self.group_string(kwargs['tournament_id'])).discard(message.reply_channel)

    @classmethod
    def group_string(cls, tournament_id):
        # Construct a unique group name for this tournament
        return "%s-%s" % (cls.group_base_string, tournament_id)

    @classmethod
    def group_send(cls, content):
        # Serialise data using Tabbycat's method + add stream for frontend ID
        group_name = cls.group_string(content.tournament.id)
        content = {
            'stream': cls.group_base_string,
            'payload': content.serialize
        }
        super().group_send(group_name, content, False)


# Send out updates upon new action log entries
@receiver(post_save, sender=ActionLogEntry)
def consumer(sender, instance, created, **kwargs):
    if created:
        ActionLogEntryConsumer.group_send(instance)
