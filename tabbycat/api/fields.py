from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.reverse import reverse


class TournamentHyperlinkedRelatedField(HyperlinkedRelatedField):
    tournament_field = 'tournament'

    def use_pk_only_optimization(self):
        return False

    def get_tournament(self, obj):
        return obj.tournament

    def get_url(self, obj, view_name, request, format):
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {
            'tournament_slug': self.get_tournament(obj).slug,
            self.lookup_url_kwarg: lookup_value,
        }
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {
            self.lookup_field: lookup_value,
        }
        return self.get_queryset().get(**lookup_kwargs)

    def get_queryset(self):
        return self.queryset.filter(**{self.tournament_field: self.context['tournament']})


class TournamentHyperlinkedIdentityField(TournamentHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class SpeakerHyperlinkedIdentityField(TournamentHyperlinkedRelatedField, HyperlinkedIdentityField):
    tournament_field = 'team__tournament'

    def get_tournament(self, obj):
        return obj.team.tournament


class AnonymisingHyperlinkedTournamentRelatedField(TournamentHyperlinkedRelatedField):

    def __init__(self, view_name=None, **kwargs):
        self.null_when = kwargs.pop('anonymous_source')
        super().__init__(view_name=view_name, **kwargs)

    def to_representation(self, value):
        if getattr(value, self.null_when, True):
            return None
        return super().to_representation(value)
