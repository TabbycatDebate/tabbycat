from django.db.models import Q
from django.forms import ModelForm, ModelMultipleChoiceField, SelectMultiple

from .models import Venue, VenueCategory


def venuecategoryform_factory(tournament):

    venue_queryset = Venue.objects.filter(Q(tournament=tournament) |
            Q(tournament__isnull=True)).order_by('name')

    class VenueCategoryForm(ModelForm):

        venues = ModelMultipleChoiceField(queryset=venue_queryset,
            widget=SelectMultiple(attrs={'size': 10}))

        class Meta:
            model = VenueCategory
            fields = ('name', 'description', 'display_in_venue_name',
                       'display_in_public_tooltip', 'venues')

    return VenueCategoryForm
