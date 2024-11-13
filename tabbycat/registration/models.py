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

    class Meta:
        abstract = True
        constraints = [UniqueConstraint(fields=['question', 'content_type', 'object_id'])]


class BooleanAnswer(Answer):
    ANSWER_TYPE = bool

    # Note: by convention, if no answer is chosen for a boolean answer, an
    # instance of this object should not be created. This way, there is no need
    # for a NullBooleanField.
    answer = models.BooleanField(verbose_name=_("answer"))

    class Meta(Answer.Meta):
        verbose_name = _("boolean answer")
        verbose_name_plural = _("boolean answers")


class IntegerAnswer(Answer):
    ANSWER_TYPE = int

    answer = models.IntegerField(verbose_name=_("answer"))

    class Meta(Answer.Meta):
        verbose_name = _("integer answer")
        verbose_name_plural = _("integer answers")


class FloatAnswer(Answer):
    ANSWER_TYPE = float

    answer = models.FloatField(verbose_name=_("answer"))

    class Meta(Answer.Meta):
        verbose_name = _("float answer")
        verbose_name_plural = _("float answers")


class StringAnswer(Answer):
    ANSWER_TYPE = str
    answer = models.TextField(verbose_name=_("answer"))

    class Meta(Answer.Meta):
        verbose_name = _("string answer")
        verbose_name_plural = _("string answers")


class ManyAnswer(Answer):
    ANSWER_TYPE = list
    answer = ArrayField(base_field=models.TextField())

    class Meta(Answer.Meta):
        verbose_name = _("multiple select answer")
        verbose_name_plural = _("multiple select answers")


class Question(models.Model):
    # When adding or changing an answer type, here are the other places you need
    # to edit:
    #   - forms.py : BaseFeedbackForm._make_question_field()
    #   - importer/importers/anorak.py : AnorakTournamentDataImporter.FEEDBACK_ANSWER_TYPES

    ANSWER_TYPE_BOOLEAN_CHECKBOX = 'bc'
    ANSWER_TYPE_BOOLEAN_SELECT = 'bs'
    ANSWER_TYPE_INTEGER_TEXTBOX = 'i'
    ANSWER_TYPE_INTEGER_SCALE = 'is'
    ANSWER_TYPE_FLOAT = 'f'
    ANSWER_TYPE_TEXT = 't'
    ANSWER_TYPE_LONGTEXT = 'tl'
    ANSWER_TYPE_SINGLE_SELECT = 'ss'
    ANSWER_TYPE_MULTIPLE_SELECT = 'ms'
    ANSWER_TYPE_CHOICES = (
        (ANSWER_TYPE_BOOLEAN_CHECKBOX, _("checkbox")),
        (ANSWER_TYPE_BOOLEAN_SELECT, _("yes/no (dropdown)")),
        (ANSWER_TYPE_INTEGER_TEXTBOX, _("integer (textbox)")),
        (ANSWER_TYPE_INTEGER_SCALE, _("integer scale")),
        (ANSWER_TYPE_FLOAT, _("float")),
        (ANSWER_TYPE_TEXT, _("text")),
        (ANSWER_TYPE_LONGTEXT, _("long text")),
        (ANSWER_TYPE_SINGLE_SELECT, _("select one")),
        (ANSWER_TYPE_MULTIPLE_SELECT, _("select multiple")),
    )
    ANSWER_TYPE_CLASSES = {
        ANSWER_TYPE_BOOLEAN_CHECKBOX: BooleanAnswer,
        ANSWER_TYPE_BOOLEAN_SELECT: BooleanAnswer,
        ANSWER_TYPE_INTEGER_TEXTBOX: IntegerAnswer,
        ANSWER_TYPE_INTEGER_SCALE: IntegerAnswer,
        ANSWER_TYPE_FLOAT: FloatAnswer,
        ANSWER_TYPE_TEXT: StringAnswer,
        ANSWER_TYPE_LONGTEXT: StringAnswer,
        ANSWER_TYPE_SINGLE_SELECT: StringAnswer,
        ANSWER_TYPE_MULTIPLE_SELECT: ManyAnswer,
    }
    ANSWER_TYPE_CLASSES_REVERSE = {
        StringAnswer: [ANSWER_TYPE_TEXT,
                                          ANSWER_TYPE_LONGTEXT,
                                          ANSWER_TYPE_SINGLE_SELECT],
        ManyAnswer: [ANSWER_TYPE_MULTIPLE_SELECT],
        IntegerAnswer:
        [ANSWER_TYPE_INTEGER_SCALE, ANSWER_TYPE_INTEGER_TEXTBOX],
        FloatAnswer: [ANSWER_TYPE_FLOAT],
        BooleanAnswer:
        [ANSWER_TYPE_BOOLEAN_SELECT, ANSWER_TYPE_BOOLEAN_CHECKBOX],
    }
    NUMERICAL_ANSWER_TYPES = [ANSWER_TYPE_INTEGER_TEXTBOX, ANSWER_TYPE_INTEGER_SCALE, ANSWER_TYPE_FLOAT]

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

    answer_type = models.CharField(max_length=2, choices=ANSWER_TYPE_CHOICES,
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

    answer_type_rels = ['stringanswer_set', 'manyanswer_set', 'integeranswer_set', 'floatanswer_set', 'booleananswer_set']

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        constraints = [UniqueConstraint(fields=['tournament', 'for_content_type', 'seq'])]

    def __str__(self):
        return self.text

    @property
    def answer_set(self):
        return getattr(self, self.answer_type_class.__name__.lower() + '_set')

    @property
    def answer_type_class(self):
        return self.ANSWER_TYPE_CLASSES[self.answer_type]

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


class QuestionMixin:
    answer_rels = ['string_answers', 'many_answers', 'integer_answers', 'float_answers', 'boolean_answers']

    def get_answers(self):
        return [
            {'question': q.question, 'answer': q.answer}
            for typ in self.answer_rels
            for q in getattr(self, typ).all()
        ]
