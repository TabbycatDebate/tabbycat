from django.contrib import admin

from .models import ActionLogEntry

# ==============================================================================
# Adjudicator Logs
# ==============================================================================


class ActionLogEntryAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'timestamp', 'get_parameters_display',
                    'tournament')
    list_filter = ('tournament', 'user', 'type')
    search_fields = ('type', 'tournament__name', 'user__username')

    def get_queryset(self, request):
        return super(ActionLogEntryAdmin,
                     self).get_queryset(request).select_related('tournament',
                                                                'user')


admin.site.register(ActionLogEntry, ActionLogEntryAdmin)
