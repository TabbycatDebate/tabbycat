from django.contrib import admin

from utils.admin import TabbycatModelAdminFieldsMixin

from .models import SentMessageRecord


@admin.register(SentMessageRecord)
class MessageLogAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'recipient', 'tournament', 'event')
    list_filter = ('round', 'method', 'event')
    ordering = ('-timestamp',)
