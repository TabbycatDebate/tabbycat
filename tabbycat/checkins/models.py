import random
from string import digits

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _
from polymorphic.models import PolymorphicModel

from utils.misc import generate_identifier_string


def generate_identifier():
    # First number should not be 0 so it is easier import into Excel etc
    new_id = str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])) + generate_identifier_string(digits, 5)
    if Identifier.objects.filter(barcode=new_id).count() == 0:
        return new_id
    else:
        return generate_identifier()


class Identifier(PolymorphicModel):
    """A unique string that will be matched to either a Person, Debate,
    or Venue (of which only Person is supported at present)"""

    instance_attr = None

    validate_alphanumeric = RegexValidator(r'^[0-9]{6}$',
        message=_("The barcode must contain exactly six digits."))
    barcode = models.CharField(unique=True, max_length=20,
        validators=[validate_alphanumeric], default=generate_identifier,
        verbose_name=_("barcode"))

    @property
    def owner(self):
        if self.instance_attr is None:
            return gettext("<Not the child instance>")
        return getattr(self, self.instance_attr)

    def __str__(self):
        return gettext("%(classname)s %(barcode)s") % {
            'classname': self.__class__.__name__,
            'barcode': str(self.barcode),
        }


class PersonIdentifier(Identifier):

    instance_attr = 'person'

    person = models.OneToOneField('participants.Person', models.CASCADE,
        verbose_name=_("person"), related_name='checkin_identifier')

    class Meta:
        verbose_name = _("person identifier")
        verbose_name_plural = _("person identifiers")


class DebateIdentifier(Identifier):

    instance_attr = 'debate'

    debate = models.OneToOneField('draw.Debate', models.CASCADE,
        verbose_name=_("debate"), related_name='checkin_identifier')

    class Meta:
        verbose_name = _("debate identifier")
        verbose_name_plural = _("debate identifiers")


class VenueIdentifier(Identifier):

    instance_attr = 'venue'

    venue = models.OneToOneField('venues.Venue', models.CASCADE,
        verbose_name=("venue"), related_name='checkin_identifier')

    class Meta:
        verbose_name = _("room identifier")
        verbose_name_plural = _("room identifiers")


class Event(models.Model):
    """A timestamped record caused by an identifier being scanned, etc."""

    identifier = models.ForeignKey(Identifier, models.CASCADE,
                                   verbose_name=_("identifier"))
    # timezone.now used over auto_add so times are visible/editable in admin
    time = models.DateTimeField(db_index=True, default=timezone.now,
                                verbose_name=_("check-in time"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
                                   verbose_name=_("tournament"))

    class Meta:
        verbose_name = _("check-in event")
        verbose_name_plural = _("check-in events")

    def serialize(self):
        return {
            'id': self.id,
            'identifier': self.identifier.barcode,
            'time': timezone.localtime(self.time).strftime("%a, %d %b %Y %H:%M:%S"),
        }
