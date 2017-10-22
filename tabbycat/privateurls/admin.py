from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import PrivateUrlSentMailRecord


@admin.register(PrivateUrlSentMailRecord)
class PrivateUrlSentMailRecordAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'get_team', 'url_type', 'email', 'url_key', 'timestamp')
    list_filter = ('url_type',)
    ordering = ('timestamp',)

    def get_team(self, obj):
        if obj.speaker:
            return obj.speaker.team
    get_team.short_description = _("Team")
