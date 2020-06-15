from django.contrib import admin
from django.db.models import Prefetch

from draw.models import DebateTeam

from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                     AdjudicatorTeamConflict, DebateAdjudicator, PreformedPanel,
                     PreformedPanelAdjudicator, TeamInstitutionConflict)


@admin.register(DebateAdjudicator)
class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
    raw_id_fields = ('debate',)

    def get_queryset(self, request):
        # can't use list_select_related class attribute, because DebateAdjudicatorManager
        # always puts a select_related on this
        return super().get_queryset(request).prefetch_related(
            Prefetch('debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
        ).select_related(
            'debate__round__tournament',
            'adjudicator__institution',
        )


@admin.register(AdjudicatorTeamConflict)
class AdjudicatorTeamConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'team')
    list_select_related = ('adjudicator__institution', 'team__tournament')
    search_fields = ('adjudicator__name', 'team__short_name', 'team__long_name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'team':
            kwargs['queryset'] = db_field.related_model.objects.select_related('tournament')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AdjudicatorAdjudicatorConflict)
class AdjudicatorAdjudicatorConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator1', 'adjudicator2')
    list_select_related = ('adjudicator1__institution', 'adjudicator2__institution')
    search_fields = ('adjudicator1__name', 'adjudicator2__name',
                     'adjudicator1__institution', 'adjudicator2__institution')


@admin.register(AdjudicatorInstitutionConflict)
class AdjudicatorInstitutionConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'institution')
    list_select_related = ('adjudicator__institution', 'institution')
    search_fields = ('adjudicator__name', 'institution__name')


@admin.register(TeamInstitutionConflict)
class TeamInstitutionConflictAdmin(admin.ModelAdmin):
    list_display = ('team', 'institution')
    list_select_related = ('team__institution', 'team__tournament', 'institution')
    search_fields = ('team__short_name', 'team__long_name', 'institution__name')


class PreformedPanelAdjudicatorInline(admin.TabularInline):
    model = PreformedPanelAdjudicator
    extra = 1
    raw_id_fields = ('adjudicator',)


@admin.register(PreformedPanel)
class PreformedPanelAdmin(admin.ModelAdmin):
    list_filter = ('round', 'round__tournament')
    list_display = ('id', 'round', 'importance', 'bracket_min', 'bracket_max', 'room_rank', 'liveness')
    list_select_related = ('round__tournament',)
    inlines = (PreformedPanelAdjudicatorInline,)
