import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now

from options.models import TournamentPreferenceModel
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=TournamentPreferenceModel)
def on_change(sender, instance: TournamentPreferenceModel, **kwargs):
    if instance.id is None:
        pass
    else:
        previous = TournamentPreferenceModel.objects.get(id=instance.id)
        if instance.name == 'all_results_released' and previous.value is False and instance.value is True:
            instance.instance.published_time = now()
            instance.instance.save()