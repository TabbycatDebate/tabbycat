from django.contrib import admin
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy, ngettext

from adjallocation.models import DebateAdjudicator
from utils.admin import TabbycatModelAdminFieldsMixin

from .models import Debate, DebateTeam


# ==============================================================================
# DebateTeam
# ==============================================================================

@admin.register(DebateTeam)
class DebateTeamAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
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
class DebateAdmin(admin.ModelAdmin):
    list_display = ('id', 'round', 'bracket', 'matchup', 'result_status', 'sides_confirmed')
    list_filter = ('round__tournament', 'round')
    list_editable = ('result_status', 'sides_confirmed')
    inlines = (DebateTeamInline, DebateAdjudicatorInline)
    raw_id_fields = ('venue',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'round__tournament',
        ).prefetch_related(
            Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team__tournament')),
            'venue__venuecategory_set',
        )

    actions = list()
    for value, verbose_name in Debate.STATUS_CHOICES:

        def _make_set_result_status(value, verbose_name): # noqa: N805
            def _set_result_status(modeladmin, request, queryset):
                count = queryset.update(result_status=value)
                message = ngettext("%(count)d debate had its status set to %(status)s.",
                    "%(count)d debates had their statuses set to %(status)s.", count) % {
                        'count': count, 'status': verbose_name}
                modeladmin.message_user(request, message)

            # so that they look different to DebateAdmin
            _set_result_status.__name__ = "set_result_status_%s" % verbose_name.lower()
            _set_result_status.short_description = gettext_lazy("Set result status to "
                    "%(status)s") % {'status': verbose_name}
            return _set_result_status

        actions.append(_make_set_result_status(value, verbose_name))
    del value, verbose_name  # for fail-fast

    def mark_as_sides_confirmed(self, request, queryset):
        updated = queryset.update(sides_confirmed=True)
        message = ngettext(
            "%(count)d debate was marked as having its sides confirmed.",
            "%(count)d debates were marked as having their sides confirmed.",
            updated,
        ) % {'count': updated}
        self.message_user(request, message)

    def mark_as_sides_not_confirmed(self, request, queryset):
        updated = queryset.update(sides_confirmed=False)
        message = ngettext(
            "%(count)d debate was marked as having its sides not confirmed.",
            "%(count)d debates were marked as having their sides not confirmed.",
            updated,
        ) % {'count': updated}
        self.message_user(request, message)

    actions.extend(['mark_as_sides_confirmed', 'mark_as_sides_not_confirmed'])
