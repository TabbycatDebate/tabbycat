from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AvailabilityConfig(AppConfig):
    name = "availability"
    verbose_name = _("Availability")
