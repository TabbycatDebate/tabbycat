from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.exceptions import ValidationError
from django.urls import NoReverseMatch, reverse

from draw.models import DebateTeam


class PrefetchedForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def __init__(self, rel, admin_site, attrs=None, using=None, queryset=None):
        self.queryset = queryset
        super().__init__(rel, admin_site, attrs=attrs, using=using)

    def get_item_label(self, obj):
        return str(obj)

    def label_and_url_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.queryset.get(**{key: value})
        except (ValueError, self.rel.model.DoesNotExist, ValidationError):
            return "", ""

        try:
            url = reverse(
                "%s:%s_%s_change"
                % (
                    self.admin_site.name,
                    obj._meta.app_label,
                    obj._meta.model_name,
                ),
                args=(obj.pk,),
            )
        except NoReverseMatch:
            url = ""  # Admin not registered for target model.

        return self.get_item_label(obj), url


class DebateTeamCompactRawIdWidget(PrefetchedForeignKeyRawIdWidget):
    """Raw ID widget using a short \"{team} in {round abbr}\" label instead of DebateTeam.__str__."""

    def get_item_label(self, obj):
        return '{} in {}'.format(obj.team.short_name, obj.debate.round.abbreviation)


class BallotSubmissionScoreInlineDebateTeamRawIdMixin:
    """Use compact DebateTeam raw-ID labels and bulk-load them once per ballot change view."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'debate_team':
            kwargs['widget'] = DebateTeamCompactRawIdWidget(
                db_field.remote_field,
                self.admin_site,
                using=kwargs.get('using'),
                queryset=DebateTeam.objects.select_related('team', 'debate__round'),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
