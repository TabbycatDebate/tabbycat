from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ParticipantsConfig(AppConfig):
    name = 'participants'
    verbose_name = _("Participants")

    def ready(self):
        from . import signals  # noqa: F401
