from django.contrib import admin

from .models import Event, Identifier


@admin.register(Identifier)
class CheckinIdentifierAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'identifier', 'object_id')
    list_filter = ('content_type',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('content_object')


@admin.register(Event)
class CheckinEventAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'time')
    list_filter = ('identifier',)
