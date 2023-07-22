from django.utils.translation import gettext_lazy as _

from options.presets import _all_subclasses

from .permissions import Permission


def all_groups():
    yield from _all_subclasses(BaseGroup)


class BaseGroup:
    name = None
    permissions = []


class Equity(BaseGroup):
    # Permissions to manage conflicts/constraints, view feedback + participant info
    name = _("Equity")
    permissions = []


class AdjudicationCore(BaseGroup):
    # Permissions to make [preformed] allocations, view feedback, and create motions
    name = _("Adjudication Core")
    permissions = []


class TabDirector(BaseGroup):
    # All permissions
    name = _("Tabulation Director")
    permissions = [p for p in Permission]


class TabAssistant(BaseGroup):
    # Permissions to match the Assistant interface
    name = _("Tabulation Assistant")
    permissions = []
