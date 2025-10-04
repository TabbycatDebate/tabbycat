import logging
from threading import Lock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Submission(models.Model):
    """Abstract base class to provide functionality common to different
    types of submissions.

    The unique_together class attribute of the Meta class MUST be set in
    all subclasses."""

    class Submitter(models.TextChoices):
        TABROOM = 'T', _("Tab room")
        PUBLIC = 'P', _("Public")
        AUTOMATION = 'A', _("Automation")

    timestamp = models.DateTimeField(auto_now_add=True,
        verbose_name=_("timestamp"))
    version = models.PositiveIntegerField(
        verbose_name=_("version"))
    submitter_type = models.CharField(max_length=1, choices=Submitter.choices,
        verbose_name=_("submitter type"))
    confirmed = models.BooleanField(default=False,
        verbose_name=_("confirmed"))

    # relevant for private URL submissions
    private_url = models.BooleanField(default=False,
        verbose_name=_("from private URL"))
    participant_submitter = models.ForeignKey('participants.Person', models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_participant_submitted",
        verbose_name=_("from participant"))

    # only relevant if submitter was in tab room
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_submitted",
        verbose_name=_("submitter"))
    confirmer = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_confirmed",
        verbose_name=_("confirmer"))
    confirm_timestamp = models.DateTimeField(blank=True, null=True,
        verbose_name=_("confirm timestamp"))
    ip_address = models.GenericIPAddressField(blank=True, null=True,
        verbose_name=_("IP address"))

    save_lock = Lock()

    class Meta:
        abstract = True

    @property
    def _unique_filter_args(self):
        if not self._meta.constraints:
            return {}
        return dict((arg, getattr(self, arg)) for arg in self._meta.constraints[0].fields
                    if arg != 'version')

    def _unique_unconfirm_args(self):
        return self._unique_filter_args

    def save(self, *args, **kwargs):
        # Use a lock to protect against the possibility that two submissions do this
        # at the same time and get the same version number or both be confirmed.
        with self.save_lock:

            # Assign the version field to one more than the current maximum version.
            if self.pk is None:
                existing = self.__class__.objects.filter(**self._unique_filter_args)
                if existing.exists():
                    self.version = existing.aggregate(models.Max('version'))['version__max'] + 1
                else:
                    self.version = 1

            # Check for uniqueness.
            if self.confirmed:
                unconfirmed = self.__class__.objects.filter(confirmed=True,
                        **self._unique_unconfirm_args()).exclude(pk=self.pk).update(confirmed=False)
                if unconfirmed > 0:
                    logger.info("Unconfirmed %d %s so that %s could be confirmed", unconfirmed, self._meta.verbose_name_plural, self)

            super(Submission, self).save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.submitter_type == self.Submitter.TABROOM and self.submitter is None:
            raise ValidationError(_("A tab room ballot must have a user associated."))
