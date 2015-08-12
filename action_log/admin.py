from django.contrib import admin

from . import models

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'timestamp', 'get_parameters_display', 'tournament')
    list_filter = ('tournament', 'user', 'type')
    search_fields = ('type', 'tournament__name', 'user__username')

    def get_queryset(self, request):
        return super(ActionLogAdmin, self).get_queryset(request).select_related(
            'tournament','user'
        )

admin.site.register(models.ActionLog, ActionLogAdmin)