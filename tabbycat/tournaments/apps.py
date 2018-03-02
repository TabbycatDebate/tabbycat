from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TournamentsConfig(AppConfig):
    name = 'tournaments'
    verbose_name = _("Tournaments")

    def ready(self):
        from . import signals  # noqa: F401
