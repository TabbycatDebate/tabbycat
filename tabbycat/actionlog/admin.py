from django.contrib import admin

from utils.admin import ModelAdmin

from .models import ActionLogEntry

# ==============================================================================
# Adjudicator Logs
# ==============================================================================


@admin.register(ActionLogEntry)
class ActionLogEntryAdmin(ModelAdmin):
    list_display = ('type', 'user', 'ip_address', 'timestamp', 'content_object',
                    'tournament', 'round')
    list_filter = ('tournament', 'user', 'type', 'content_type', 'round')
    search_fields = ('type', 'user__username')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tournament', 'round', 'round__tournament', 'user').prefetch_related('content_object')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_queryset(self, request, queryset):
        return False
