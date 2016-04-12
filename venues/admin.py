from django.contrib import admin

from .models import VenueGroup, Venue


class VenueGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'team_capacity')
    search_fields = ('name', )


admin.site.register(VenueGroup, VenueGroupAdmin)


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'priority', 'tournament')
    list_filter = ('group', 'priority', 'tournament')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super(VenueAdmin,
                     self).get_queryset(request).select_related('group')


admin.site.register(Venue, VenueAdmin)
