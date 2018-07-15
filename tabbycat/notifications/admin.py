from django.contrib import admin

from utils.admin import TabbycatModelAdminFieldsMixin

from .models import MessageSentRecord


@admin.register(MessageSentRecord)
class MessageLogAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'recepient', 'tournament', 'event')
    list_filter = ('round', 'method', 'event')
    ordering = ('timestamp',)
