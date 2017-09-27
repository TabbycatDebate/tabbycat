from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ActionLogConfig(AppConfig):
    name = 'actionlog'
    verbose_name = _("Action Log")
