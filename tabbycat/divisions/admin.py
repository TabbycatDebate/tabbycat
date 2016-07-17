from django.contrib import admin

from .models import Division


# ==============================================================================
# Division
# ==============================================================================

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'venue_group', 'time_slot')
    list_filter = ('tournament', 'venue_group')
    search_fields = ('name', )
    ordering = ('tournament', 'name', )


admin.site.register(Division, DivisionAdmin)
