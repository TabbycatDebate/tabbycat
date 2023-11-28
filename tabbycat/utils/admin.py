from django.contrib import admin
from django.contrib.admin.options import get_content_type_for_model
from django.utils.translation import gettext_lazy as _

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
            change_message=self.add_ip_to_message(request, message),
        )


class TabbycatModelAdminFieldsMixin:

    @admin.display(description=_("Round"))
    def get_round(self, obj):
        if hasattr(obj, 'debate'):
            return obj.debate.round.name
        else:
            return obj.debate_team.debate.round.name

    @admin.display(description=_("Team"))
    def get_team(self, obj):
        return obj.debate_team.team

    @admin.display(description=_("Speaker"))
    def get_speaker_name(self, obj):
        return obj.speaker.name

    @admin.display(description=_("Tournament"))
    def get_tournament(self, obj):
        if hasattr(obj, 'round'):
            return obj.round.tournament
        else:
            return obj.debate.round.tournament

    @admin.display(description=_("Side"))
    def get_team_side(self, obj):
        return obj.debate_team.side

    @admin.display(description=_("Motion"))
    def get_motion_ref(self, obj):
        return obj.motion.reference

    @admin.display(description=_("Confirmed"))
    def get_confirmed(self, obj):
        return obj.ballot_submission.confirmed

    @admin.display(description=_("Adjudicator"))
    def get_adj_name(self, obj):
        return obj.debate_adjudicator.adjudicator.name


def custom_titled_filter(title):
    class Wrapper(admin.RelatedFieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper
