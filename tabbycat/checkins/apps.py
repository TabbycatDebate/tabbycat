from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CheckinsConfig(AppConfig):
    name = 'checkins'
    verbose_name = _("Check-Ins")
