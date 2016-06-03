from django.contrib import admin

from .models import ActiveVenue, ActiveTeam, ActiveAdjudicator

# ==============================================================================
# ActiveVenue
# ==============================================================================


class ActiveVenueAdmin(admin.ModelAdmin):
    list_display = ('venue', 'round')
    search_fields = ('venue', )
    list_filter = ('venue', 'round')

admin.site.register(ActiveVenue, ActiveVenueAdmin)

# ==============================================================================
# ActiveTeam
# ==============================================================================


class ActiveTeamAdmin(admin.ModelAdmin):
    list_display = ('team', 'round')
    search_fields = ('team', )
    list_filter = ('team', 'round')

admin.site.register(ActiveTeam, ActiveTeamAdmin)

# ==============================================================================
# ActiveAdjudicator
# ==============================================================================


class ActiveAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'round')
    search_fields = ('adjudicator', )
    list_filter = ('adjudicator', 'round')

admin.site.register(ActiveAdjudicator, ActiveAdjudicatorAdmin)
