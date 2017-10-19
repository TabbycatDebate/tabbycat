from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PrivateUrlsConfig(AppConfig):
    name = 'privateurls'
    verbose_name = _("Private URL Management")
