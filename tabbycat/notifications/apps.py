from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    name = 'notifications'
    verbose_name = _("Notifications")

    def ready(self):
        from anymail.signals import tracking

        from .email_tracking import record_tracking_event
        tracking.connect(record_tracking_event, dispatch_uid='notifications_record_tracking_event')
