from itertools import groupby

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, ngettext, ngettext_lazy

from adjallocation.models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                                  AdjudicatorTeamConflict, TeamInstitutionConflict)
from adjfeedback.models import AdjudicatorBaseScoreHistory
from availability.admin import RoundAvailabilityInline
from breakqual.models import BreakCategory
from draw.models import TeamSideAllocation
from tournaments.models import Tournament
from utils.admin import ModelAdmin
from venues.admin import VenueConstraintInline

from .emoji import pick_unused_emoji, populate_code_names_from_emoji, set_emoji
from .models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team


# ==============================================================================
# Region
# ==============================================================================

@admin.register(Region)
class RegionAdmin(ModelAdmin):
    pass


# ==============================================================================
# Institution
# ==============================================================================

@admin.register(Institution)
class InstitutionAdmin(ModelAdmin):
    list_display = ('name', 'code', 'region')
    list_select_related = ('region',)
    ordering = ('name', )
    search_fields = ('name', )


# ==============================================================================
# Speaker
# ==============================================================================

@admin.register(Speaker)
class SpeakerAdmin(ModelAdmin):
    list_filter = ('team__tournament', 'team__institution')
    list_display = ('name', 'team', 'gender')
    search_fields = ('name', 'team__short_name', 'team__long_name',
                     'team__institution__name', 'team__institution__code')
    raw_id_fields = ('team', )


# ==============================================================================
# Speaker
# ==============================================================================

@admin.register(SpeakerCategory)
class SpeakerCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'seq', 'tournament', 'limit', 'public')
    list_filter = ('tournament', )
    ordering = ('tournament', 'seq')


# ==============================================================================
# Teams
# ==============================================================================

class SpeakerInline(admin.TabularInline):
    model = Speaker
    fields = ('name', 'email', 'gender')


class TeamSideAllocationInline(admin.TabularInline):
    model = TeamSideAllocation


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def clean_url_key(self):
        # So that the url key can be unique and be blank
        return self.cleaned_data['url_key'] or None

    def clean_break_categories(self):
        categories = self.cleaned_data['break_categories']
        tournament = self.cleaned_data.get('tournament')
        if tournament is None:
            return categories  # don't add more errors if there isn't even a tournament
        for bc in categories:
            if bc.tournament != tournament:
                self.add_error('break_categories', ValidationError(
                    _("The team can't be in a break category of a different tournament. Please remove: %(category)s"),
                    code='invalid_break_category', params={'category': str(bc)},
                ))
        return categories


class TeamInstitutionConflictInline(admin.TabularInline):
    model = TeamInstitutionConflict
    extra = 1


class AdjudicatorTeamConflictInline(admin.TabularInline):
    model = AdjudicatorTeamConflict
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'team':
            kwargs["queryset"] = Team.objects.select_related('tournament')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    form = TeamForm
    list_display = ('long_name', 'short_name', 'emoji_code', 'institution',
                    'tournament')
    search_fields = ('reference', 'short_name', 'code_name', 'institution__name',
                     'institution__code', 'tournament__name')
    list_filter = ('tournament', 'institution', 'break_categories')
    inlines = (SpeakerInline, TeamSideAllocationInline, VenueConstraintInline,
               AdjudicatorTeamConflictInline, TeamInstitutionConflictInline,
               RoundAvailabilityInline)
    actions = ['delete_url_key', 'assign_emoji', 'assign_code_names']

    def get_queryset(self, request):
        # can't use select_related, because TeamManager always puts a select_related on this
        return super().get_queryset(request).select_related('tournament')

    @admin.display(description=_("Emoji & Code"))
    def emoji_code(self, obj):
        return "%s %s" % (obj.emoji or '-', obj.code_name)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'emoji' and kwargs.get("initial") is None:
            kwargs["initial"] = pick_unused_emoji()[0]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if (db_field.name == 'break_categories' and kwargs.get("initial") is None and
                Tournament.objects.count() == 1):
            kwargs["initial"] = BreakCategory.objects.filter(is_general=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @admin.display(description=_("Delete URL Key"))
    def delete_url_key(self, request, queryset):
        num_speakers = Speaker.objects.filter(team__in=queryset).update(url_key=None)
        for obj in queryset:
            self.log_change(request, obj, [{"changed": {"fields": [{"speaker": ["url_key"]}]}}])
        message = ngettext_lazy(
            "%(count)d speaker had their URL key removed.",
            "%(count)d speakers had their URL keys removed.",
            num_speakers) % {'count': num_speakers}
        self.message_user(request, message)

    @admin.display(description=_("Reset emoji"))
    def assign_emoji(self, request, queryset):
        count = queryset.update(emoji=None)
        for tournament, teams in groupby(queryset.select_related('tournament').order_by('tournament_id'), lambda t: t.tournament):
            set_emoji(list(teams), tournament)
            for team in teams:
                self.log_change(request, team, [{"changed": {"fields": ["emoji"]}}])

        message = ngettext_lazy(
            "%(count)d team had their emoji reset.",
            "%(count)d teams had their emojis reset.",
            count) % {'count': count}
        self.message_user(request, message)

    @admin.display(description=_("Reset code name"))
    def assign_code_names(self, request, queryset):
        count = populate_code_names_from_emoji(queryset, overwrite=True)
        for obj in queryset:
            self.log_change(request, obj, [{"changed": {"fields": ["code_name"]}}])

        message = ngettext_lazy(
            "%(count)d team had their code name reset.",
            "%(count)d teams had their code names reset.",
            count) % {'count': count}
        self.message_user(request, message)


# ==============================================================================
# Adjudicator
# ==============================================================================

class AdjudicatorAdjudicatorConflictInline(admin.TabularInline):
    model = AdjudicatorAdjudicatorConflict
    fk_name = "adjudicator1"
    extra = 1
    raw_id_fields = ('adjudicator2',)


class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = AdjudicatorInstitutionConflict
    extra = 1


class AdjudicatorBaseScoreHistoryInline(admin.TabularInline):
    model = AdjudicatorBaseScoreHistory
    extra = 1


class AdjudicatorForm(forms.ModelForm):
    class Meta:
        model = Adjudicator
        fields = '__all__'

    def clean_url_key(self):
        # So that the url key can be unique and be blank
        return self.cleaned_data['url_key'] or None


@admin.register(Adjudicator)
class AdjudicatorAdmin(ModelAdmin):
    form = AdjudicatorForm
    list_display = ('name', 'institution', 'tournament', 'trainee',
                    'independent', 'adj_core', 'gender', 'base_score')
    search_fields = ('name', 'tournament__name', 'institution__name', 'institution__code')
    list_filter = ('tournament', 'institution')
    list_editable = ('independent', 'adj_core', 'trainee', 'base_score')
    inlines = (AdjudicatorTeamConflictInline, AdjudicatorInstitutionConflictInline,
               AdjudicatorAdjudicatorConflictInline, AdjudicatorBaseScoreHistoryInline,
               RoundAvailabilityInline)
    actions = ['delete_url_key']

    def get_queryset(self, request):
        # can't use select_related, because TeamManager always puts a select_related on this
        return super().get_queryset(request).select_related('tournament')

    @admin.display(description=_("Delete URL Key"))
    def delete_url_key(self, request, queryset):
        updated = queryset.update(url_key=None)
        for obj in queryset:
            self.log_change(request, obj, [{"changed": {"fields": ["url_key"]}}])
        message = ngettext(
            "%(count)d adjudicator had their URL key removed.",
            "%(count)d adjudicators had their URL keys removed.",
            updated,
        ) % {'count': updated}
        self.message_user(request, message)
