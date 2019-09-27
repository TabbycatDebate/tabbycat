from django.contrib import admin
from django.utils import timezone

from utils.admin import TabbycatModelAdminFieldsMixin

from .models import BulkNotification, EmailStatus, SentMessage


def precise_timestamp_isoformat(model, field_name):
    def precise_timestamp(self, obj):
        return timezone.localtime(getattr(obj, field_name)).isoformat()
    precise_timestamp.short_description = model._meta.get_field(field_name).verbose_name
    return precise_timestamp


@admin.register(SentMessage)
class SentMessageAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('recipient', 'email', 'precise_timestamp', 'notification')
    list_filter = ('notification__round', 'method', 'notification__event')
    search_fields = ('message_id', 'recipient__name', 'email', 'recipient__email')
    ordering = ('-notification',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'notification__tournament')

    precise_timestamp = precise_timestamp_isoformat(SentMessage, 'timestamp')


@admin.register(BulkNotification)
class BulkNotificationAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('precise_timestamp', 'event', 'round', 'tournament')
    list_filter = ('tournament', 'round', 'event')
    ordering = ('-timestamp',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('round__tournament', 'tournament')

    precise_timestamp = precise_timestamp_isoformat(BulkNotification, 'timestamp')


@admin.register(EmailStatus)
class EmailStatusAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('email', 'event', 'precise_timestamp')
    list_filter = ('event',)
    ordering = ('-timestamp',)
    search_fields = ('email__message_id', 'email__recipient__name', 'email__email', 'email__recipient__email')

    precise_timestamp = precise_timestamp_isoformat(EmailStatus, 'timestamp')
