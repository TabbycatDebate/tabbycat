from django.contrib import admin
from django.contrib.admin.options import get_content_type_for_model

from .misc import get_ip_address

""" General utilities for extending filters/lists in the admin area """

# ==============================================================================
# Utilities
# ==============================================================================


class ModelAdmin(admin.ModelAdmin):

    def add_ip_to_message(self, request, message):
        ip_address = get_ip_address(request)
        if type(message) is list:  # JSON
            message.append({'identity': {'ip': ip_address}})
        else:
            message += "\nIP: %s" % (ip_address,)
        return message

    def log_addition(self, request, object, message):
        return super().log_addition(request, object, self.add_ip_to_message(request, message))

    def log_change(self, request, object, message):
        return super().log_change(request, object, self.add_ip_to_message(request, message))

    def log_deletion(self, request, object, object_repr, message=[]):
        from django.contrib.admin.models import DELETION, LogEntry
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
            message=self.add_ip_to_message(request, message),
        )


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
