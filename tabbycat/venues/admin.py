from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from gfklookupwidget.widgets import GfkLookupWidget

from availability.admin import RoundAvailabilityInline

from .models import Venue, VenueCategory, VenueConstraint


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'priority', 'tournament', 'categories_list')
    list_filter = ('venuecategory', 'priority', 'tournament')
    search_fields = ('name',)
    inlines = (RoundAvailabilityInline,)

    def categories_list(self, obj):
        return ", ".join([c.name for c in obj.venuecategory_set.all()])

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
                'tournament').prefetch_related('venuecategory_set')


@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_in_venue_name',
            'display_in_public_tooltip', 'venues_list')
    ordering = ('name',)

    def venues_list(self, obj):
        return ", ".join([v.name for v in obj.venues.all()])

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('venues')


class VenueConstraintModelForm(forms.ModelForm):
    class Meta(object):
        model = VenueConstraint
        fields = '__all__'
        widgets = {
            'subject_id': GfkLookupWidget(
                content_type_field_name='subject_content_type',
                parent_field=VenueConstraint._meta.get_field('subject_content_type'),
            ),
        }


@admin.register(VenueConstraint)
class VenueConstraintAdmin(admin.ModelAdmin):
    form = VenueConstraintModelForm
    list_display = ('subject', 'category', 'priority')
    search_fields = ('adjudicator__name', 'adjudicator__institution__code',
            'adjudicator__institution__name', 'team__short_name', 'team__long_name',
            'institution__name', 'institution__code',
            'category__name', 'priority')
    list_filter = ('subject_content_type', 'category', 'priority')
    ordering = ('subject_content_type', 'category')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('subject')


# Used in participants/admin.py
class VenueConstraintInline(GenericTabularInline):
    model = VenueConstraint
    ct_field = 'subject_content_type'
    ct_fk_field = 'subject_id'
    extra = 6
