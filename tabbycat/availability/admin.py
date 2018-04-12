from django.contrib import admin

from .models import RoundAvailability


@admin.register(RoundAvailability)
class RoundAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'round')
    list_filter = ('content_type', 'round')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('content_object')
