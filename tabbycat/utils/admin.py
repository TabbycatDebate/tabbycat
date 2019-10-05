from django.contrib import admin

""" General utilities for extending filters/lists in the admin area """

# ==============================================================================
# Utilities
# ==============================================================================


class TabbycatModelAdminFieldsMixin:

    def get_round(self, obj):
        if hasattr(obj, 'debate'):
            return obj.debate.round.name
        else:
            return obj.debate_team.debate.round.name
    get_round.short_description = 'Round'

    def get_team(self, obj):
        return obj.debate_team.team
    get_team.short_description = 'Team'

    def get_speaker_name(self, obj):
        return obj.speaker.name
    get_speaker_name.short_description = 'Speaker'

    def get_tournament(self, obj):
        if hasattr(obj, 'round'):
            return obj.round.tournament
        else:
            return obj.debate.round.tournament

    get_tournament.short_description = 'Tournament'

    def get_team_side(self, obj):
        return obj.debate_team.side
    get_team_side.short_description = 'Side'

    def get_motion_ref(self, obj):
        return obj.motion.reference
    get_motion_ref.short_description = 'Motion'

    def get_confirmed(self, obj):
        return obj.ballot_submission.confirmed
    get_confirmed.short_description = 'Confirmed'

    def get_adj_name(self, obj):
        return obj.debate_adjudicator.adjudicator.name
    get_adj_name.short_description = "Adjudicator"


def custom_titled_filter(title):
    class Wrapper(admin.RelatedFieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper
