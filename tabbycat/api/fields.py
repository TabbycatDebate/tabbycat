from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField
from rest_framework.reverse import reverse

from participants.models import Team


class TournamentHyperlinkedIdentityField(HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {
            'tournament_slug': obj.tournament.slug,
            self.lookup_url_kwarg: lookup_value,
        }
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {
            'tournament__slug': view_kwargs['tournament_slug'],
            self.lookup_field: lookup_value,
        }
        return self.get_queryset().get(**lookup_kwargs)

class InstitutionTeamRelationalField(PrimaryKeyRelatedField):

    def get_queryset(self):
        return Team.objects.filter(tournament=self.context['tournament'])