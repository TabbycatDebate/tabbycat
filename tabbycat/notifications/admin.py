from django.contrib import admin

from utils.admin import TabbycatModelAdminFieldsMixin

from .models import BulkNotification, EmailStatus, SentMessageRecord


@admin.register(SentMessageRecord)
class SentMessageRecordAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('recipient', 'notification')
    list_filter = ('notification__round', 'method', 'notification__event')
    ordering = ('-notification',)


@admin.register(BulkNotification)
class BulkNotificationAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'event', 'tournament')
    list_filter = ('tournament', 'round', 'event')
    ordering = ('-timestamp',)


@admin.register(EmailStatus)
class EmailStatusAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('email', 'event', 'timestamp')
    list_filter = ('event',)
    ordering = ('-timestamp',)
