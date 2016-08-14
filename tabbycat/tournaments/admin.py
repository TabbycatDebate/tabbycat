from django.contrib import admin

from .models import Round, Tournament


# ==============================================================================
# Tournament
# ==============================================================================

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'seq', 'emoji', 'short_name', 'current_round')
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

    def _construct_message_for_user(self, request, count, action, **kwargs):
        message_bit = "1 round was " if count == 1 else "{:d} rounds were ".format(count)
        self.message_user(request, message_bit + action, **kwargs)

    def mark_as_silent(self, request, queryset):
        updated = queryset.update(silent=True)
        self._construct_message_for_user(request, updated, "marked as silent.")

    def mark_as_not_silent(self, request, queryset):
        updated = queryset.update(silent=False)
        self._construct_message_for_user(request, updated, "marked as not silent.")

    def release_motions(self, request, queryset):
        updated = queryset.update(motions_released=True)
        self._construct_message_for_user(request, updated, "marked as motions released.")

    def unrelease_motions(self, request, queryset):
        updated = queryset.update(motions_released=False)
        self._construct_message_for_user(request, updated, "marked as motions not released.")

    for value, verbose_name in Round.STATUS_CHOICES:

        def _make_set_draw_status(value, verbose_name):
            def _set_draw_status(modeladmin, request, queryset):
                count = queryset.update(draw_status=value)
                message_bit = "1 round had its" if count == 1 else "{:d} rounds had their".format(
                    count)
                modeladmin.message_user(
                    request, message_bit + " draw status set to " + verbose_name)

            # so that they look different to RoundAdmin
            _set_draw_status.__name__ = "set_draw_status_%s" % verbose_name.lower()
            _set_draw_status.short_description = "Set draw status to %s" % verbose_name.lower()
            return _set_draw_status

        actions.append(_make_set_draw_status(value, verbose_name))
    del value, verbose_name  # for fail-fast

admin.site.register(Round, RoundAdmin)
