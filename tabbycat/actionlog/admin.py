from django.contrib import admin

from .models import ActionLogEntry

# ==============================================================================
# Adjudicator Logs
# ==============================================================================


@admin.register(ActionLogEntry)
class ActionLogEntryAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'ip_address', 'timestamp', 'content_object',
                    'tournament', 'round')
    list_filter = ('tournament', 'user', 'type', 'content_type', 'round')
    search_fields = ('type', 'user__username')

    def get_queryset(self, request):
        return super(ActionLogEntryAdmin, self).get_queryset(request).select_related(
            'tournament', 'round', 'round__tournament', 'user').prefetch_related('content_object')
