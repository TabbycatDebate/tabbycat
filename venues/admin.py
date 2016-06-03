from django.contrib import admin

from .models import (
    VenueGroup, Venue, TeamVenueConstraint, AdjudicatorVenueConstraint,
    InstitutionVenueConstraint, DivisionVenueConstraint)


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


# ==============================================================================
# VenueConstraint models
# ==============================================================================

class BaseVenueConstraintAdmin(admin.ModelAdmin):
    associate_field = None

    common_list_display = ('venue_group', 'priority')
    common_search_fields = ('venue_group', 'priority')
    common_list_filter = ('venue_group', 'priority')

    def get_list_display(self, request):
        return (self.associate_field,) + self.common_list_display

    def get_search_fields(self, request):
        return (self.associate_field,) + self.common_search_fields

    def get_list_filter(self, request):
        return (self.associate_field,) + self.common_list_filter

    @property
    def raw_id_fields(self):
        return (self.associate_field,)


@admin.register(TeamVenueConstraint)
class TeamVenueConstraintAdmin(BaseVenueConstraintAdmin):
    associate_field = 'team'


@admin.register(AdjudicatorVenueConstraint)
class AdjudicatorVenueConstraintAdmin(BaseVenueConstraintAdmin):
    associate_field = 'adjudicator'


@admin.register(InstitutionVenueConstraint)
class InstitutionVenueConstraintAdmin(BaseVenueConstraintAdmin):
    associate_field = 'institution'


@admin.register(DivisionVenueConstraint)
class DivisionVenueConstraintAdmin(BaseVenueConstraintAdmin):
    associate_field = 'division'
