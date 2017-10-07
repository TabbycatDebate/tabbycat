from django.contrib import admin
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _

from .models import Round, Tournament


# ==============================================================================
# Tournament
# ==============================================================================

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'seq', 'short_name', 'current_round', 'active')
    ordering = ('seq', )


admin.site.register(Tournament, TournamentAdmin)


# ==============================================================================
# Round
# ==============================================================================

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage',
                    'draw_type', 'draw_status', 'feedback_weight', 'silent',
                    'motions_released', 'starts_at')
    list_filter = ('tournament', )
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type',
                     'draw_status')
    actions = ['mark_as_silent', 'mark_as_not_silent', 'release_motions', 'unrelease_motions']

    def mark_as_silent(self, request, queryset):
        updated = queryset.update(silent=True)
        message = ungettext(
            "%(count)d round was marked as silent.",
            "%(count)d rounds were marked as silent.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    mark_as_silent.short_description = _("Mark as silent")

    def mark_as_not_silent(self, request, queryset):
        updated = queryset.update(silent=False)
        message = ungettext(
            "%(count)d round was marked as not silent.",
            "%(count)d rounds were marked as not silent.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    mark_as_not_silent.short_description = _("Mark as not silent")

    def release_motions(self, request, queryset):
        updated = queryset.update(motions_released=True)
        message = ungettext(
            "%(count)d round was marked as motions released.",
            "%(count)d rounds were marked as motions released.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    release_motions.short_description = _("Release motions")

    def unrelease_motions(self, request, queryset):
        updated = queryset.update(motions_released=False)
        message = ungettext(
            "%(count)d round was marked as motions not released.",
            "%(count)d rounds were marked as motions not released.",
            updated
        ) % {'count': updated}
        self.message_user(request, message)
    unrelease_motions.short_description = _("Unrelease motions")

    for value, verbose_name in Round.STATUS_CHOICES:

        def _make_set_draw_status(value, verbose_name):
            def _set_draw_status(modeladmin, request, queryset):
                count = queryset.update(draw_status=value)
                message = ungettext(
                    "%(count)d round had its draw status set to %(status)s.",
                    "%(count)d rounds had their draw status set to %(status)s.",
                    count
                ) % {'count': count, 'status': verbose_name.lower()}
                modeladmin.message_user(request, message)

            # so that they look different to RoundAdmin
            _set_draw_status.__name__ = "set_draw_status_%s" % value.lower()
            _set_draw_status.short_description = _("Set draw status to %(status)s") % \
                    {'status': verbose_name.lower()}
            return _set_draw_status

        actions.append(_make_set_draw_status(value, verbose_name))
    del value, verbose_name  # for fail-fast

admin.site.register(Round, RoundAdmin)
