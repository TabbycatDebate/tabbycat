from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResultsConfig(AppConfig):
    name = 'results'
    verbose_name = _("Results")
