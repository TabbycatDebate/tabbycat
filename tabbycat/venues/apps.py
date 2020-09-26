from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VenuesConfig(AppConfig):
    name = 'venues'
    verbose_name = _("Rooms")
