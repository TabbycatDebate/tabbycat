from django.db.models import Q
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField, SlugRelatedField
from rest_framework.reverse import reverse

from participants.models import Speaker


class TournamentHyperlinkedRelatedField(HyperlinkedRelatedField):
    default_tournament_field = 'tournament'

    def __init__(self, *args, **kwargs):
        self.tournament_field = kwargs.pop('tournament_field', self.default_tournament_field)
        super().__init__(*args, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def get_tournament(self, obj):
        return obj.tournament

    def get_url_kwargs(self, obj):
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {
            'tournament_slug': self.get_tournament(obj).slug,
            self.lookup_url_kwarg: lookup_value,
        }
        return kwargs

    def get_url(self, obj, view_name, request, format):
        return reverse(view_name, kwargs=self.get_url_kwargs(obj), request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {
            self.lookup_field: lookup_value,
        }
        return self.get_queryset().get(**lookup_kwargs)

    def lookup_kwargs(self):
        return {self.tournament_field: self.context['tournament']}

    def get_queryset(self):
        return super().get_queryset().filter(**self.lookup_kwargs()).select_related(self.tournament_field)


class TournamentHyperlinkedIdentityField(TournamentHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class RoundHyperlinkedRelatedField(TournamentHyperlinkedRelatedField):
    default_tournament_field = 'round__tournament'
    round_field = 'round'

    def get_tournament(self, obj):
        return self.get_round(obj).tournament

    def get_round(self, obj):
        return obj.round

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs['round_seq'] = self.get_round(obj).seq
        return kwargs

    def lookup_kwargs(self):
        return {self.round_field: self.context['round']}

    def get_queryset(self):
        return super().get_queryset().select_related(self.round_field)


class RoundHyperlinkedIdentityField(RoundHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class DebateHyperlinkedIdentityField(RoundHyperlinkedIdentityField):
    default_tournament_field = 'debate__round__tournament'
    round_field = 'debate__round'

    def get_round(self, obj):
        return obj.debate.round

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs['debate_pk'] = obj.debate.pk
        return kwargs

    def lookup_kwargs(self):
        return {'debate': self.context['debate']}

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class AnonymisingHyperlinkedTournamentRelatedField(TournamentHyperlinkedRelatedField):
    default_tournament_field = 'team__tournament'

    def __init__(self, view_name=None, queryset=Speaker.objects.all(), **kwargs):
        self.null_when = kwargs.pop('anonymous_source')
        super().__init__(view_name=view_name, queryset=queryset, **kwargs)

    def to_representation(self, value):
        if getattr(value, self.null_when, True):
            return None
        return super().to_representation(value)


class MotionHyperlinkedRelatedField(RoundHyperlinkedRelatedField):
    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs.pop('round_seq')
        return kwargs


class MotionHyperlinkedIdentityField(MotionHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class AdjudicatorFeedbackIdentityField(RoundHyperlinkedIdentityField):
    default_tournament_field = None
    round_field = None

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs.pop('round_seq')
        return kwargs

    def lookup_kwargs(self):
        return {}  # More complicated lookup than with kwargs

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(source_adjudicator__debate__round=self.context['round']) | Q(source_team__debate__round=self.context['round']))


class CreatableSlugRelatedField(SlugRelatedField):
    def to_internal_value(self, data):
        try:
            # get_or_create returns (obj, created?) - only want the object
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')
