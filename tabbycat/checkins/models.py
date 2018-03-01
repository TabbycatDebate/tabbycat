import random
import string

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Identifier(models.Model):
    """ A unique string that will be matched to either a Person, Debate,
    or Venue (of which only Person is supported at present)"""

    barID = RegexValidator(r'^[0-9a-zA-Z]{6,}$',
                           'Only up 6 alphanumeric characters are allowed.')
    identifier = models.CharField(unique=True, max_length=6, validators=[barID])

    CONTENT_TYPE_CHOICES = models.Q(app_label='draw', model='debate') | \
                           models.Q(app_label='participants', model='person') | \
                           models.Q(app_label='venues', model='venue')
    content_type = models.ForeignKey(ContentType, models.CASCADE,
                                     limit_choices_to=CONTENT_TYPE_CHOICES,
                                     verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _("check-in identifier")
        verbose_name_plural = _("check-in identifiers")

    def get_random_string(self):
        allowed_chars = ''.join((string.ascii_letters, string.digits))
        unique_id = ''.join(random.choice(allowed_chars) for _ in range(32))
        return unique_id # Will need to check for collisions


class Event(models.Model):
    """ A time stamped record caused by an identifier being scanned/etc """

    identifier = models.ForeignKey(Identifier, models.CASCADE,
                                   verbose_name=_("identifier"))
    # timezone.now used over auto_add so times are visible/editable in admin
    time = models.DateTimeField(db_index=True, default=timezone.now,
                                verbose_name=_("checkin"))

    class Meta:
        verbose_name = _("check-in event")
        verbose_name_plural = _("check-in events")
