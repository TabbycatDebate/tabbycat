from django.contrib import admin

from adjallocation.models import DebateAdjudicator
from utils.admin import TabbycatModelAdminFieldsMixin

from .models import Debate, DebateTeam


# ==============================================================================
# DebateTeam
# ==============================================================================

class DebateTeamAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('team', 'get_tournament', 'get_round', 'position')
    search_fields = ('team', )
    raw_id_fields = ('debate', 'team', )

    def get_queryset(self, request):
        return super(DebateTeamAdmin,
                     self).get_queryset(request).select_related(
                         'debate__round', 'debate__round__tournament')


admin.site.register(DebateTeam, DebateTeamAdmin)


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


class DebateAdmin(admin.ModelAdmin):
    list_display = ('id', 'round', 'bracket', 'aff_team', 'neg_team',
                    'result_status')
    list_filter = ('round__tournament', 'round', 'division')
    inlines = (DebateTeamInline, DebateAdjudicatorInline)
    raw_id_fields = ('venue', 'division')

    def get_queryset(self, request):
        return super(DebateAdmin, self).get_queryset(request).select_related(
            'round__tournament', 'division__tournament', 'venue__group')

    actions = list()
    for value, verbose_name in Debate.STATUS_CHOICES:

        def _make_set_result_status(value, verbose_name):
            def _set_result_status(modeladmin, request, queryset):
                count = queryset.update(result_status=value)
                message_bit = "1 debate had its" if count == 1 else "{:d} debates had their".format(
                    count)
                modeladmin.message_user(
                    request, message_bit + " status set to " + verbose_name)

            # so that they look different to DebateAdmin
            _set_result_status.__name__ = "set_result_status_%s" % verbose_name.lower()
            _set_result_status.short_description = "Set result status to %s" % verbose_name.lower()
            return _set_result_status

        actions.append(_make_set_result_status(value, verbose_name))
    del value, verbose_name  # for fail-fast


admin.site.register(Debate, DebateAdmin)
