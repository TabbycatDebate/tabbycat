from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdjFeedbackConfig(AppConfig):
    name = 'adjfeedback'
    verbose_name = _("Adjudicator Feedback")
