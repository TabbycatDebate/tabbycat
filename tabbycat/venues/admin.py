from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from gfklookupwidget.widgets import GfkLookupWidget

from .models import Venue, VenueCategory, VenueConstraint, VenueConstraintCategory, VenueGroup


@admin.register(VenueGroup)
class VenueGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_name', 'priority', 'tournament')
    list_filter = ('group', 'priority', 'tournament')
    search_fields = ('name',)

    def group_name(self, obj):
        if obj.group is None:
            return None
        return obj.group.name
    group_name.short_description = 'Venue Group'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('group')


@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_in_venue_name',
            'display_in_public_tooltip', 'venues_list')

    def venues_list(self, obj):
        return ", ".join([v.name for v in obj.venues.all()])


# ==============================================================================
# VenueConstraint models
# ==============================================================================

class VenueConstraintModelForm(forms.ModelForm):
    class Meta(object):
        model = VenueConstraint
        fields = '__all__'
        widgets = {
            'subject_id': GfkLookupWidget(
                content_type_field_name='subject_content_type',
                parent_field=VenueConstraint._meta.get_field('subject_content_type'),
            )
        }


@admin.register(VenueConstraint)
class VenueConstraintAdmin(admin.ModelAdmin):
    form = VenueConstraintModelForm
    list_display = ('subject', 'category', 'priority')
    search_fields = ('adjudicator__name', 'adjudicator__institution__code',
            'adjudicator__institution__name', 'team__short_name', 'team__long_name',
            'institution__name', 'institution__code', 'division__name',
            'category__name', 'priority')
    list_filter = ('subject_content_type', 'category', 'priority')
    ordering = ('subject_content_type', 'category')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('subject')


class VenueConstraintInline(GenericTabularInline):
    model = VenueConstraint
    ct_field = 'subject_content_type'
    ct_fk_field = 'subject_id'
    extra = 6


@admin.register(VenueConstraintCategory)
class VenueConstraintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'venues_list')

    def venues_list(self, obj):
        return ", ".join([v.name for v in obj.venues.all()])
