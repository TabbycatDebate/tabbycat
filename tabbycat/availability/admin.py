from django.contrib import admin

from .models import RoundAvailability


class RoundAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'round')
    search_fields = ('content_object', 'round')
    list_filter = ('content_type', 'round')

admin.site.register(RoundAvailability, RoundAvailabilityAdmin)
