from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from . import models
from debate.models import Debate, DebateTeam, Adjudicator, DebateAdjudicator, Round, Team
from debate.forms import OptionalChoiceField

# General, but only used here

class IntegerRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    """Used by IntegerRadioSelect."""
    outer_html = '<table{id_attr} class="feedback-integer-scale-table"><tr>{content}</tr></table>'
    inner_html = '<td>{choice_value}{sub_widgets}</td>'

class IntegerRadioSelect(forms.RadioSelect):
    renderer = IntegerRadioFieldRenderer

class IntegerScaleField(forms.IntegerField):
    """Class to do integer scale fields."""
    widget = IntegerRadioSelect

    def __init__(self, *args, **kwargs):
        super(IntegerScaleField, self).__init__(*args, **kwargs)
        self.widget.choices = tuple((i, str(i)) for i in range(self.min_value, self.max_value+1))

class BlankUnknownBooleanSelect(forms.NullBooleanSelect):
    """Uses '--------' instead of 'Unknown' for the None choice."""

    def __init__(self, attrs=None):
        choices = (('1', ugettext_lazy('--------')),
                   ('2', ugettext_lazy('Yes')),
                   ('3', ugettext_lazy('No')))
        # skip the NullBooleanSelect constructor
        super(forms.NullBooleanSelect, self).__init__(attrs, choices)

class BooleanSelectField(forms.NullBooleanField):
    """Widget to do boolean select fields following our conventions.
    Specifically, if 'required', checks that an option was chosen."""
    widget = BlankUnknownBooleanSelect
    def clean(self, value):
        value = super(BooleanSelectField, self).clean(value)
        if self.required and value is None:
            raise forms.ValidationError(_("This field is required."))
        return value

class RequiredTypedChoiceField(forms.TypedChoiceField):
    def clean(self, value):
        value = super(RequiredTypedChoiceField, self).clean(value)
        if value == "None":
            raise forms.ValidationError(_("This field is required."))
        return value

# Feedback Fields

class AdjudicatorFeedbackCheckboxFieldRenderer(forms.widgets.CheckboxFieldRenderer):
    """Used by AdjudicatorFeedbackCheckboxSelectMultiple."""
    outer_html = '<div{id_attr} class="feedback-multiple-select">{content}</div>'
    inner_html = '<div class="feedback-option">{choice_value}{sub_widgets}</div>'

class AdjudicatorFeedbackCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    renderer = AdjudicatorFeedbackCheckboxFieldRenderer

class AdjudicatorFeedbackCheckboxSelectMultipleField(forms.MultipleChoiceField):
    """Class to do multiple choice fields following our conventions.
    Specifically, converts to a string rather than a list."""
    widget = AdjudicatorFeedbackCheckboxSelectMultiple

    def clean(self, value):
        value = super(AdjudicatorFeedbackCheckboxSelectMultipleField, self).clean(value)
        return models.AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR.join(value)

# Feedback Forms

class BaseFeedbackForm(forms.Form):
    """Base class for all dynamically-created feedback forms. Contains all
    question fields."""

    # parameters set at "compile time" by subclasses
    tournament = NotImplemented
    _use_tournament_password = False
    _confirm_on_submit = False
    _enforce_required = True
    question_filter = dict()

    def __init__(self, *args, **kwargs):
        super(BaseFeedbackForm, self).__init__(*args, **kwargs)
        self._create_fields()

    def _make_question_field(self, question):
        if question.answer_type == question.ANSWER_TYPE_BOOLEAN_SELECT:
            field = BooleanSelectField()
        elif question.answer_type == question.ANSWER_TYPE_BOOLEAN_CHECKBOX:
            field = forms.BooleanField()
        elif question.answer_type == question.ANSWER_TYPE_INTEGER_TEXTBOX:
            min_value = int(question.min_value) if question.min_value else None
            max_value = int(question.max_value) if question.max_value else None
            field = forms.IntegerField(min_value=min_value, max_value=max_value)
        elif question.answer_type == question.ANSWER_TYPE_INTEGER_SCALE:
            min_value = int(question.min_value) if question.min_value is not None else None
            max_value = int(question.max_value) if question.max_value is not None else None
            if min_value is None or max_value is None:
                logger.error("Integer scale %r has no min_value or no max_value" % question.reference)
                field = forms.IntegerField()
            else:
                field = IntegerScaleField(min_value=min_value, max_value=max_value)
        elif question.answer_type == question.ANSWER_TYPE_FLOAT:
            field = forms.FloatField(min_value=question.min_value,
                    max_value=question.max_value)
        elif question.answer_type == question.ANSWER_TYPE_TEXT:
            field = forms.CharField()
        elif question.answer_type == question.ANSWER_TYPE_LONGTEXT:
            field = forms.CharField(widget=forms.Textarea)
        elif question.answer_type == question.ANSWER_TYPE_SINGLE_SELECT:
            field = OptionalChoiceField(choices=question.choices_for_field)
        elif question.answer_type == question.ANSWER_TYPE_MULTIPLE_SELECT:
            field = AdjudicatorFeedbackCheckboxSelectMultipleField(choices=question.choices_for_field)
        field.label = question.text
        field.required = self._enforce_required and question.required
        return field

    def _create_fields(self):
        """Creates dynamic fields in the form."""
        # Feedback questions defined for the tournament
        adj_min_score = self.tournament.config.get('adj_min_score')
        adj_max_score = self.tournament.config.get('adj_max_score')
        score_label = mark_safe("Overall score<br />(%s=lowest, %s=highest)" % (adj_min_score, adj_max_score))
        self.fields['score'] = forms.FloatField(min_value=adj_min_score, max_value=adj_max_score, label=score_label)

        for question in self.tournament.adj_feedback_questions.filter(**self.question_filter):
            self.fields[question.reference] = self._make_question_field(question)

        # Tournament password field, if applicable
        if self._use_tournament_password and self.tournament.config.get('public_use_password'):
            self.fields['password'] = TournamentPasswordField(tournament=self.tournament)

    def save_adjudicatorfeedback(self, **kwargs):
        """Saves the question fields and returns the AdjudicatorFeedback.
        To be called by save() of child classes."""
        af = models.AdjudicatorFeedback(**kwargs)

        if self._confirm_on_submit:
            self.discard_all_existing(adjudicator=kwargs['adjudicator'],
                    source_adjudicator=kwargs['source_adjudicator'],
                    source_team=kwargs['source_team'])
            af.confirmed = True

        af.score = self.cleaned_data['score']
        af.save()

        for question in self.tournament.adj_feedback_questions.filter(**self.question_filter):
            if self.cleaned_data[question.reference] is not None:
                answer = question.answer_type_class(feedback=af, question=question,
                        answer=self.cleaned_data[question.reference])
                answer.save()

        return af

    def discard_all_existing(self, **kwargs):
        for fb in models.AdjudicatorFeedback.objects.filter(**kwargs):
            fb.discarded = True
            fb.save()

def make_feedback_form_class(source, *args, **kwargs):
    """Constructs a FeedbackForm class specific to the given source.
    'source' is the Adjudicator or Team who is giving feedback.
    'submission_fields' is a dict of fields that is passed directly as keyword
        arguments to Submission.
    'confirm_on_submit' is a bool, and indicates that this feedback should be
        as confirmed and all others discarded."""
    if isinstance(source, Adjudicator):
        return make_feedback_form_class_for_adj(source, *args, **kwargs)
    elif isinstance(source, Team):
        return make_feedback_form_class_for_team(source, *args, **kwargs)
    else:
        raise TypeError('source must be Adjudicator or Team: %r' % source)

def make_feedback_form_class_for_adj(source, submission_fields, confirm_on_submit=False, enforce_required=True):
    """Constructs a FeedbackForm class specific to the given source adjudicator.
    Parameters are as for make_feedback_form_class."""

    def adj_choice(da):
        return (da.id, '%s (%s, %s)' % (da.adjudicator.name,
                da.debate.round.name, da.get_type_display()))
    def coerce_da(value):
        return DebateAdjudicator.objects.get(id=int(value))

    debate_filter = dict(debateadjudicator__adjudicator=source,
            round__draw_status=Round.STATUS_RELEASED)
    if not source.tournament.config.get('panellist_feedback_enabled'): # then include only debates for which this adj was the chair
        debate_filter['debateadjudicator__type'] = DebateAdjudicator.TYPE_CHAIR
    debates = Debate.objects.filter(**debate_filter)

    choices = [(None, '-- Adjudicators --')]
    # for an adjudicator, find every adjudicator on their panel except them
    choices.extend(adj_choice(da) for da in DebateAdjudicator.objects.filter(
        debate__in=debates).exclude(
        adjudicator=source).select_related(
        'debate').order_by(
        '-debate__round__seq'))

    class FeedbackForm(BaseFeedbackForm):
        tournament = source.tournament  # BaseFeedbackForm setting
        _use_tournament_password = True # BaseFeedbackForm setting
        _confirm_on_submit = confirm_on_submit
        _enforce_required = enforce_required
        question_filter = dict(chair_on_panellist=True)

        debate_adjudicator = RequiredTypedChoiceField(choices=choices, coerce=coerce_da)

        def save(self):
            """Saves the form and returns the AdjudicatorFeedback object."""
            da = self.cleaned_data['debate_adjudicator']
            sa = DebateAdjudicator.objects.get(adjudicator=source, debate=da.debate)
            kwargs = dict(adjudicator=da.adjudicator, source_adjudicator=sa, source_team=None)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm

def make_feedback_form_class_for_team(source, submission_fields, confirm_on_submit=False, enforce_required=True):
    """Constructs a FeedbackForm class specific to the given source team.
    Parameters are as for make_feedback_form_class."""

    # Only include non-silent rounds for teams.
    debates = Debate.objects.filter(debateteam__team=source, round__silent=False,
        round__draw_status=Round.STATUS_RELEASED).order_by('-round__seq')

    choices = [(None, '-- Adjudicators --')]
    for debate in debates:
        try:
            chair = DebateAdjudicator.objects.get(debate=debate, type=DebateAdjudicator.TYPE_CHAIR)
        except DebateAdjudicator.DoesNotExist:
            continue
        panel = DebateAdjudicator.objects.filter(debate=debate, type=DebateAdjudicator.TYPE_PANEL)
        if panel.exists():
            choices.append((chair.id, '{name} ({r} - chair gave oral)'.format(
                name=chair.adjudicator.name, r=debate.round.name)))
            for da in panel:
                choices.append((da.id, '{name} ({r} - chair rolled, this panellist gave oral)'.format(
                    name=da.adjudicator.name, r=debate.round.name)))
        else:
            choices.append((chair.id, '{name} ({r})'.format(
                name=chair.adjudicator.name, r=debate.round.name)))

    def coerce_da(value):
        return DebateAdjudicator.objects.get(id=int(value))

    class FeedbackForm(BaseFeedbackForm):
        tournament = source.tournament  # BaseFeedbackForm setting
        _use_tournament_password = True # BaseFeedbackForm setting
        _confirm_on_submit = confirm_on_submit
        _enforce_required = enforce_required
        question_filter = dict(team_on_orallist=True)

        debate_adjudicator = RequiredTypedChoiceField(choices=choices, coerce=coerce_da)

        def save(self):
            # Saves the form and returns the m.AdjudicatorFeedback object
            da = self.cleaned_data['debate_adjudicator']
            st = DebateTeam.objects.get(team=source, debate=da.debate)
            kwargs = dict(adjudicator=da.adjudicator, source_adjudicator=None, source_team=st)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm

