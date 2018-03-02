from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DrawConfig(AppConfig):
    name = 'draw'
    verbose_name = _("Draw")
