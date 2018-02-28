from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PrivateUrlsConfig(AppConfig):
    name = 'privateurls'
    verbose_name = _("Private URL Management")
