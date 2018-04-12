from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MotionsConfig(AppConfig):
    name = 'motions'
    verbose_name = _("Motions")
