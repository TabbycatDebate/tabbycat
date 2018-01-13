from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _

from draw.models import TeamSideAllocation
from adjallocation.models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict, AdjudicatorInstitutionConflict
from adjfeedback.models import AdjudicatorTestScoreHistory
from breakqual.models import BreakCategory
from tournaments.models import Tournament
from venues.admin import VenueConstraintInline

from .emoji import pick_unused_emoji
from .models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team


# ==============================================================================
# Region
# ==============================================================================

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


# ==============================================================================
# Institution
# ==============================================================================

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    ordering = ('name', )
    search_fields = ('name', )


# ==============================================================================
# Speaker
# ==============================================================================

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_filter = ('team__tournament',)
    list_display = ('name', 'team', 'gender')
    search_fields = ('name', )
    raw_id_fields = ('team', )


# ==============================================================================
# Speaker
# ==============================================================================

@admin.register(SpeakerCategory)
class SpeakerCategoryAdmin(admin.ModelAdmin):
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
                    code='invalid_break_category', params={'category': str(bc)}
                ))
        return categories


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    list_display = ('long_name', 'short_name', 'emoji', 'institution',
                    'division', 'tournament')
    search_fields = ('reference', 'short_name', 'institution__name',
                     'institution__code', 'tournament__name')
    list_filter = ('tournament', 'division', 'institution', 'break_categories')
    inlines = (SpeakerInline, TeamSideAllocationInline, VenueConstraintInline)
    raw_id_fields = ('division', )
    actions = ['delete_url_key']

    def get_queryset(self, request):
        return super(TeamAdmin, self).get_queryset(request).prefetch_related(
            'institution', 'division')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'emoji' and kwargs.get("initial") is None:
            kwargs["initial"] = pick_unused_emoji()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if (db_field.name == 'break_categories' and kwargs.get("initial") is None and
                Tournament.objects.count() == 1):
            kwargs["initial"] = BreakCategory.objects.filter(is_general=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def delete_url_key(self, request, queryset):
        updated = queryset.update(url_key=None)
        message = ungettext(
            "%(count)d team had its URL key removed.",
            "%(count)d teams had their URL keys removed.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    delete_url_key.short_description = _("Delete URL key")


# ==============================================================================
# Adjudicator
# ==============================================================================

class AdjudicatorConflictInline(admin.TabularInline):
    model = AdjudicatorConflict
    extra = 1
    verbose_name_plural = "Adjudicator team conflicts"


class AdjudicatorAdjudicatorConflictInline(admin.TabularInline):
    model = AdjudicatorAdjudicatorConflict
    fk_name = "adjudicator"
    extra = 1
    raw_id_fields = ('conflict_adjudicator', )


class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = AdjudicatorInstitutionConflict
    extra = 1


class AdjudicatorTestScoreHistoryInline(admin.TabularInline):
    model = AdjudicatorTestScoreHistory
    extra = 1


class AdjudicatorForm(forms.ModelForm):
    class Meta:
        model = Adjudicator
        fields = '__all__'

    def clean_url_key(self):
        # So that the url key can be unique and be blank
        return self.cleaned_data['url_key'] or None


@admin.register(Adjudicator)
class AdjudicatorAdmin(admin.ModelAdmin):
    form = AdjudicatorForm
    list_display = ('name', 'institution', 'tournament', 'trainee',
                    'independent', 'adj_core', 'gender')
    search_fields = ('name', 'tournament__name', 'institution__name', 'institution__code')
    list_filter = ('tournament', 'name', 'institution')
    inlines = (AdjudicatorConflictInline, AdjudicatorInstitutionConflictInline,
               AdjudicatorAdjudicatorConflictInline, AdjudicatorTestScoreHistoryInline)
    actions = ['delete_url_key']

    def delete_url_key(self, request, queryset):
        updated = queryset.update(url_key=None)
        message = ungettext(
            "%(count)d adjudicator had their URL key removed.",
            "%(count)d adjudicators had their URL keys removed.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    delete_url_key.short_description = _("Delete URL key")
