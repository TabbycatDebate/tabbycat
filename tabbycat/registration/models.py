from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField

from utils.models import UniqueConstraint


CONTENT_TYPE_CHOICES = models.Q(app_label='adjfeedback', model='adjudicatorfeedback') | \
                       models.Q(app_label='participants', model='tournamentinstitution') | \
                       models.Q(app_label='participants', model='speaker') | \
                       models.Q(app_label='participants', model='adjudicator') | \
                       models.Q(app_label='participants', model='coach') | \
                       models.Q(app_label='participants', model='person') | \
                       models.Q(app_label='participants', model='team')


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
