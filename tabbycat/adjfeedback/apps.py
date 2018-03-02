from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdjFeedbackConfig(AppConfig):
    name = 'adjfeedback'
    verbose_name = _("Adjudicator Feedback")
