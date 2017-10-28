from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import PrivateUrlSentMailRecord


@admin.register(PrivateUrlSentMailRecord)
class PrivateUrlSentMailRecordAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'get_team', 'url_type', 'email', 'url_key', 'timestamp')
    list_filter = ('url_type',)
    ordering = ('timestamp',)
    search_fields = ('email', 'speaker__name', 'adjudicator__name')

    def get_team(self, obj):
        if obj.speaker:
            return obj.speaker.team
        # else return None
    get_team.short_description = _("Team")
