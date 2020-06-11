from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = _("Application Programming Interface")

    def ready(self):
        from . import signals  # noqa: F401
