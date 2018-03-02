from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdjAllocationConfig(AppConfig):
    name = 'adjallocation'
    verbose_name = _("Adjudicator Allocation")
