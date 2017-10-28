from django.contrib import admin

from .models import RoundAvailability


class RoundAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'round')
    list_filter = ('content_type', 'round')

admin.site.register(RoundAvailability, RoundAvailabilityAdmin)
