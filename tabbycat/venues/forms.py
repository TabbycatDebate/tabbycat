from django.forms import ModelForm, ModelMultipleChoiceField, SelectMultiple

from .models import VenueCategory


def venuecategoryform_factory(venues_queryset):

    venue_choices = [(venue.id, venue.display_name) for venue in venues_queryset]

    class VenueCategoryForm(ModelForm):

        venues = ModelMultipleChoiceField(queryset=venues_queryset,
            widget=SelectMultiple(attrs={'size': 10}))
        venues.choices = venue_choices  # can't be passed as keyword argument

        class Meta:
            model = VenueCategory
            fields = ('name', 'description', 'display_in_venue_name',
                       'display_in_public_tooltip', 'rotate', 'venues')

    return VenueCategoryForm
