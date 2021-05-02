from django.contrib import admin

from .models import DebateIdentifier, Event, PersonIdentifier, VenueIdentifier


@admin.register(PersonIdentifier)
class PersonIdentifierAdmin(admin.ModelAdmin):
    base_model = PersonIdentifier
    list_display = ('person', 'barcode')
    list_filter = ('person__adjudicator__institution', 'person__speaker__team__institution')
    search_fields = ('person__name', 'person__adjudicator__institution__name',
        'person__speaker__team__institution__name')


@admin.register(DebateIdentifier)
class DebateIdentifierAdmin(admin.ModelAdmin):
    base_model = DebateIdentifier
    list_display = ('debate', 'barcode')
    list_filter = ('debate__round',)
    search_fields = ('debate__debateteam__team__short_name', 'debate__debateteam__team__long_name')


@admin.register(VenueIdentifier)
class VenueIdentifierAdmin(admin.ModelAdmin):
    base_model = VenueIdentifier
    list_display = ('venue', 'barcode')
    list_filter = ('venue__venuecategory',)
    search_fields = ('venue__name', 'venue__venuecategory__name')


@admin.register(Event)
class CheckinEventAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'polymorphic_ctype', 'checkin_time')
    list_filter = ('identifier', 'identifier__polymorphic_ctype')

    def polymorphic_ctype(self, obj):
        return obj.identifier.polymorphic_ctype.model

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(None).prefetch_related('identifier__polymorphic_ctype')

    def checkin_time(self, obj):
        return obj.time.strftime("%d %b %Y %H:%M:%S.%f")
