from django.contrib import admin
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _, ngettext

from adjallocation.models import DebateAdjudicator
from utils.admin import ModelAdmin, TabbycatModelAdminFieldsMixin

from .models import Debate, DebateTeam


# ==============================================================================
# DebateTeam
# ==============================================================================

@admin.register(DebateTeam)
class DebateTeamAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('team', 'side', 'debate', 'get_tournament', 'get_round')
    search_fields = ('team__long_name', 'team__short_name', 'team__institution__name', 'team__institution__code', 'flags')
    raw_id_fields = ('debate', 'team')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'debate__round__tournament',
            'team__tournament',
        ).prefetch_related(
            Prefetch('debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
        )


# ==============================================================================
# Debate
# ==============================================================================

class DebateTeamInline(admin.TabularInline):
    model = DebateTeam
    extra = 1
    raw_id_fields = ('team', )


class DebateAdjudicatorInline(admin.TabularInline):
    model = DebateAdjudicator
    extra = 1


@admin.register(Debate)
class DebateAdmin(ModelAdmin):
    list_display = ('id', 'round', 'bracket', 'matchup', 'result_status', 'sides_confirmed')
    list_filter = ('round__tournament', 'round')
    list_editable = ('result_status', 'sides_confirmed')
    inlines = (DebateTeamInline, DebateAdjudicatorInline)
    raw_id_fields = ('venue',)
    actions = ('mark_as_sides_confirmed', 'mark_as_sides_not_confirmed')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'round__tournament',
        ).prefetch_related(
            Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team__tournament')),
            'venue__venuecategory_set',
        )

    def mark_as_sides_confirmed(self, request, queryset):
        updated = queryset.update(sides_confirmed=True)
        for obj in queryset:
            self.log_change(request, obj, [{"changed": {"fields": ["sides_confirmed"]}}])
        message = ngettext(
            "%(count)d debate was marked as having its sides confirmed.",
            "%(count)d debates were marked as having their sides confirmed.",
            updated,
        ) % {'count': updated}
        self.message_user(request, message)

    @admin.display(description=_("Mark sides as not confirmed"))
    def mark_as_sides_not_confirmed(self, request, queryset):
        updated = queryset.update(sides_confirmed=False)
        for obj in queryset:
            self.log_change(request, obj, [{"changed": {"fields": ["sides_confirmed"]}}])
        message = ngettext(
            "%(count)d debate was marked as having its sides not confirmed.",
            "%(count)d debates were marked as having their sides not confirmed.",
            updated,
        ) % {'count': updated}
        self.message_user(request, message)
