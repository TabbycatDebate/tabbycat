from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField

from results.submission_model import Submission
from utils.models import UniqueConstraint

from .types import Currency


CONTENT_TYPE_CHOICES = models.Q(app_label='adjfeedback', model='adjudicatorfeedback') | \
                       models.Q(app_label='participants', model='tournamentinstitution') | \
                       models.Q(app_label='participants', model='speaker') | \
                       models.Q(app_label='participants', model='adjudicator') | \
                       models.Q(app_label='participants', model='coach') | \
                       models.Q(app_label='participants', model='person') | \
                       models.Q(app_label='participants', model='team')

PARTICIPANT_TYPE_CHOICES = models.Q(app_label='participants', model='speaker') | \
                           models.Q(app_label='participants', model='adjudicator') | \
                           models.Q(app_label='participants', model='team') | \
                           models.Q(app_label='participants', model='institution')


class Answer(models.Model):

    content_type = models.ForeignKey(ContentType, models.CASCADE,
        limit_choices_to=CONTENT_TYPE_CHOICES,
        verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.ForeignKey('Question', models.CASCADE,
        verbose_name=_("question"))
    answer = models.TextField(verbose_name=_("answer"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            UniqueConstraint(fields=['question', 'content_type', 'object_id']),
        ]


class Question(models.Model):
    # When adding or changing an answer type, here are the other places you need
    # to edit:
    #   - forms.py : BaseFeedbackForm._make_question_field()
    #   - importer/importers/anorak.py : AnorakTournamentDataImporter.FEEDBACK_ANSWER_TYPES

    class AnswerType(models.TextChoices):
        BOOLEAN_CHECKBOX = 'bc', _("checkbox")
        BOOLEAN_SELECT = 'bs', _("yes/no (dropdown)")
        INTEGER_TEXTBOX = 'i', _("integer (textbox)")
        INTEGER_SCALE = 'is', _("integer scale")
        FLOAT = 'f', _("float")
        TEXT = 't', _("text")
        LONGTEXT = 'tl', _("long text")
        SINGLE_SELECT = 'ss', _("select one")
        MULTIPLE_SELECT = 'ms', _("select multiple")
        DATETIME = 'dt', _("date + time")

    ANSWER_TYPE_TYPES = {
        AnswerType.BOOLEAN_CHECKBOX: bool,
        AnswerType.BOOLEAN_SELECT: bool,
        AnswerType.INTEGER_TEXTBOX: int,
        AnswerType.INTEGER_SCALE: int,
        AnswerType.FLOAT: float,
        AnswerType.TEXT: str,
        AnswerType.LONGTEXT: str,
        AnswerType.SINGLE_SELECT: str,
        AnswerType.MULTIPLE_SELECT: list,
        AnswerType.DATETIME: datetime,
    }

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    for_content_type = models.ForeignKey(ContentType, models.CASCADE,
        limit_choices_to=CONTENT_TYPE_CHOICES,
        verbose_name=_("for content type"))
    seq = models.IntegerField(help_text="The order in which questions are displayed",
        verbose_name=_("sequence number"))
    text = models.CharField(max_length=255,
        verbose_name=_("text"),
        help_text=_("The question displayed to participants, e.g., \"Did you agree with the decision?\""))
    help_text = models.CharField(verbose_name=_("help text"), blank=True,
        help_text=_("Additional context for the question"))
    name = models.CharField(max_length=30,
        verbose_name=_("name"),
        help_text=_("A short name for the question, e.g., \"Agree with decision\""))

    answer_type = models.CharField(max_length=2, choices=AnswerType.choices,
        verbose_name=_("answer type"))
    required = models.BooleanField(default=True,
        verbose_name=_("required"),
        help_text=_("Whether participants are required to fill out this field"))
    min_value = models.FloatField(blank=True, null=True,
        verbose_name=_("minimum value"),
        help_text=_("Minimum allowed value for numeric fields (ignored for text or boolean fields)"))
    max_value = models.FloatField(blank=True, null=True,
        verbose_name=_("maximum value"),
        help_text=_("Maximum allowed value for numeric fields (ignored for text or boolean fields)"))

    choices = ArrayField(
        base_field=models.TextField(),
        blank=True,
        verbose_name=_("choices"),
        help_text=_("Permissible choices for select one/multiple fields (ignored for other fields)"),
        default=list)

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        constraints = [UniqueConstraint(fields=['tournament', 'for_content_type', 'seq'])]

    def __str__(self):
        return self.text

    @property
    def choices_for_field(self):
        return tuple((x, x) for x in self.choices)

    @property
    def choices_for_number_scale(self):
        return self.construct_number_scale(self.min_value, self.max_value)

    def construct_number_scale(self, min_value, max_value):
        """Used to build up a semi-intelligent range of options for numeric scales.
        Shifted here rather than the class so that it can be more easily used to
        construct the default values for printed forms."""
        step = max((int(max_value) - int(min_value)) / 10, 1)
        options = list(range(int(min_value), int(max_value + 1), int(step)))
        return options


class Invitation(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))
    for_content_type = models.ForeignKey(ContentType, models.CASCADE, limit_choices_to=PARTICIPANT_TYPE_CHOICES,
        verbose_name=_("for content type"))
    institution = models.ForeignKey('participants.Institution', models.CASCADE, null=True, blank=True, verbose_name=_("institution"))
    team = models.ForeignKey('participants.Team', models.CASCADE, null=True, blank=True, verbose_name=_("team"))
    url_key = models.CharField(max_length=50, verbose_name=_("URL key"))
    created_on = models.DateTimeField(auto_now=True, verbose_name=_("created on"))

    class Meta:
        verbose_name = _("invitation")
        verbose_name_plural = _("invitations")
        constraints = [UniqueConstraint(fields=['tournament', 'url_key'])]

    def __str__(self):
        return '%s: %s invitation (%s)' % (self.tournament.name, self.for_content_type, self.team or self.institution)


class ArbitraryDecimalField(models.DecimalField):
    def _check_decimal_places(self, **kwargs):
        return []

    def _check_max_digits(self, **kwargs):
        return []

    def _check_decimal_places_and_max_digits(self, **kwargs):
        return []

    def db_type(self, connection):
        # pg or bust
        assert connection.settings_dict["ENGINE"] == "django.db.backends.postgresql"
        return "numeric"


class PaymentConnection(models.Model):
    class Platform(models.TextChoices):
        STRIPE = 's', "Stripe"
        PAYPAL = 'p', "PayPal"

    class Status(models.TextChoices):
        CONNECTED = 'c', _("connected")
        DISCONNECTED = 'd', _("disconnected")
        PENDING = 'p', _("pending")

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE)
    platform = models.CharField(max_length=1, choices=Platform.choices)
    external_id = models.CharField()
    status = models.CharField(max_length=1, choices=Status.choices)

    class Meta:
        verbose_name = _("payment connection")
        verbose_name_plural = _("payment connections")
        constraints = [UniqueConstraint(fields=['tournament', 'platform'])]


class PriceItem(models.Model):

    class ItemType(models.TextChoices):
        PARTICIPANT = 'p', _("participant registration")
        ADJUDICATOR = 'a', _("adjudicator registration")
        TEAM = 't', _("team registration")
        SPEAKER = 's', _("speaker registration")
        OBSERVER = 'o', _("observer registration")
        MISSING_ADJ = 'm', _("missing adjudicator fee")
        OTHER = '', _("custom fee")

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))
    item_type = models.CharField(max_length=1, choices=ItemType.choices, null=True, blank=True,
        verbose_name=_("item type"),
        help_text=_("If an option is selected, the item will be auto-populated in invoices where applicable"))
    name = models.CharField(max_length=100, blank=True,
        verbose_name=_("name"),
        help_text=_("Optional; overrides the default name from the item's type"))
    amount = ArbitraryDecimalField(verbose_name=_("amount"))
    currency = models.CharField(max_length=3, choices=Currency.choices, verbose_name=_("currency"))
    stripe_product_id = models.CharField(null=True, blank=True, unique=True, verbose_name=_("Stripe product ID"))
    stripe_price_id = models.CharField(null=True, blank=True, unique=True, verbose_name=_("Stripe price ID"))
    active = models.BooleanField(default=True, blank=True, verbose_name=_("active"), help_text=_("Should the item be applied to future invoices?"))

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")


class PaymentScheduleEvent(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    due_date = models.DateTimeField(auto_now=False, verbose_name=_("due date"))
    percentage_required = models.FloatField(
        verbose_name=_("percentage required"),
        help_text=_("The cumulative percentage of the invoice to be paid by the time"))

    class Meta:
        verbose_name = _("payment schedule event")
        verbose_name_plural = _("payment schedule events")


class Invoice(models.Model):
    class Status(models.TextChoices):
        VOID = 'v', _("Void")
        OPEN = 'o', _("Open")
        PAID = 'p', _("Paid")

    amount = ArbitraryDecimalField()
    currency = models.CharField(choices=Currency.choices)
    tournament = models.ForeignKey('tournaments.Tournament', models.PROTECT)
    date_posted = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
    from_registration = models.BooleanField(default=True)

    status = models.CharField(max_length=1, choices=Status.choices)
    amount_paid = ArbitraryDecimalField()

    institution = models.ForeignKey('participants.Institution', models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('participants.Team', models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey('participants.Person', models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")


class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(PriceItem, models.PROTECT)
    quantity = models.PositiveIntegerField()
    note = models.TextField()

    date_added = models.DateTimeField(auto_now_add=True)

    institution = models.ForeignKey('participants.Institution', models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('participants.Team', models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey('participants.Person', models.SET_NULL, null=True, blank=True)


class Payment(Submission):
    class Method(models.TextChoices):
        CASH = 'c', _("cash")
        WIRE = 'w', _("wire")
        OTHER = '', _("other")
        STRIPE = 's', "Stripe"
        PAYPAL = 'p', "PayPal"

    class Status(models.TextChoices):
        COMPLETED = 'c', _("Completed")
        REFUNDED = 'r', _("Refunded")
        FAILED = 'f', _("Failed")
        ON_HOLD = 'h', _("On hold")
        EXPIRED = 'e', _("Expired")
        PENDING = 'p', _("Pending")

    reference = models.CharField()
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = ArbitraryDecimalField()
    tournament = models.ForeignKey('tournaments.Tournament', models.PROTECT)
    currency = models.CharField(choices=Currency.choices)
    method = models.CharField(max_length=1, choices=Method.choices)
    status = models.CharField(max_length=1, choices=Status.choices)

    institution = models.ForeignKey('participants.Institution', models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('participants.Team', models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey('participants.Person', models.SET_NULL, null=True, blank=True)

    invoices = models.ManyToManyField(Invoice, through='InvoicePayment')

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        constraints = []


class InvoicePayment(models.Model):
    invoice = models.ForeignKey(Invoice, models.PROTECT)
    payment = models.ForeignKey(Payment, models.PROTECT)
    amount = ArbitraryDecimalField()
    currency = models.CharField(choices=Currency.choices)

    class Meta:
        verbose_name = _("invoice payment")
        verbose_name_plural = _("invoice payments")


class Discount(Submission):
    tournament = models.ForeignKey('tournaments.Tournament', models.PROTECT)
    amount = ArbitraryDecimalField()
    currency = models.CharField(choices=Currency.choices)
    note = models.TextField(blank=True)

    institution = models.ForeignKey('participants.Institution', models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('participants.Team', models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey('participants.Person', models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("discount")
        verbose_name_plural = _("discounts")


class LineDiscount(models.Model):
    invoice = models.ForeignKey(Invoice, models.CASCADE)
    discount = models.ForeignKey(Discount, models.PROTECT)


class SlotTransfer(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))
    from_institution = models.ForeignKey('participants.Institution', models.CASCADE, related_name="from_institution_set", verbose_name=_("from institution"))
    to_institution = models.ForeignKey('participants.Institution', models.CASCADE, related_name='to_institution_set', verbose_name=_("to institution"))
    for_content_type = models.ForeignKey(ContentType, models.PROTECT,
        limit_choices_to=CONTENT_TYPE_CHOICES,
        verbose_name=_("for content type"))
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("slot transfer")
        verbose_name_plural = _("slot transfers")
