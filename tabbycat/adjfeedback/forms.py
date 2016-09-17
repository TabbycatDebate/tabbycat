import logging

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Team
from results.forms import TournamentPasswordField
from tournaments.models import Round
from utils.forms import OptionalChoiceField

from .models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from .utils import expected_feedback_targets

logger = logging.getLogger(__name__)

ADJUDICATOR_POSITION_NAMES = {
    AdjudicatorAllocation.POSITION_CHAIR: 'chair',
    AdjudicatorAllocation.POSITION_ONLY: 'solo',
    AdjudicatorAllocation.POSITION_PANELLIST: 'panellist',
    AdjudicatorAllocation.POSITION_TRAINEE: 'trainee'
}


# ==============================================================================
# General, but only used here
# ==============================================================================

class IntegerRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    """Used by IntegerRadioSelect."""
    outer_html = '<div{id_attr} class="flex-horizontal">{content}</div>'
    inner_html = '<div class="flex-1 text-center">{choice_value}{sub_widgets}</div>'


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
        choices = (
            ('1', '--------'),
            # Translators: Please leave this blank, it should be left for the base Django translations.
            ('2', ugettext_lazy('Yes')),
            # Translators: Please leave this blank, it should be left for the base Django translations.
            ('3', ugettext_lazy('No'))
        )
        # skip the NullBooleanSelect constructor
        super(forms.NullBooleanSelect, self).__init__(attrs, choices)


class BooleanSelectField(forms.NullBooleanField):
    """Widget to do boolean select fields following our conventions.
    Specifically, if 'required', checks that an option was chosen."""
    widget = BlankUnknownBooleanSelect

    def clean(self, value):
        value = super(BooleanSelectField, self).clean(value)
        if self.required and value is None:
            # Translators: Please leave this blank, it should be left for the base Django translations.
            raise forms.ValidationError(_("This field is required."))
        return value


class RequiredTypedChoiceField(forms.TypedChoiceField):
    def clean(self, value):
        value = super(RequiredTypedChoiceField, self).clean(value)
        if value == "None":
            # Translators: Please leave this blank, it should be left for the base Django translations.
            raise forms.ValidationError(_("This field is required."))
        return value


# ==============================================================================
# Feedback Fields
# ==============================================================================

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
        return AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR.join(value)


# ==============================================================================
# Feedback Forms
# ==============================================================================

class BaseFeedbackForm(forms.Form):
    """Base class for all dynamically-created feedback forms. Contains all
    question fields."""

    # parameters set at "compile time" by subclasses
    _tournament = None  # must be set by subclasses
    _use_tournament_password = False
    _confirm_on_submit = False
    _enforce_required = True
    question_filter = dict()

    def __init__(self, *args, **kwargs):
        super(BaseFeedbackForm, self).__init__(*args, **kwargs)
        self._create_fields()

    @staticmethod
    def coerce_target(value):
        debate_id, adj_id = value.split('-')
        debate = Debate.objects.get(id=int(debate_id))
        adjudicator = Adjudicator.objects.get(id=int(adj_id))
        return debate, adjudicator

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
            field = forms.FloatField(min_value=question.min_value, max_value=question.max_value)
        elif question.answer_type == question.ANSWER_TYPE_TEXT:
            field = forms.CharField()
        elif question.answer_type == question.ANSWER_TYPE_LONGTEXT:
            field = forms.CharField(widget=forms.Textarea)
        elif question.answer_type == question.ANSWER_TYPE_SINGLE_SELECT:
            field = OptionalChoiceField(choices=question.choices_for_field)
        elif question.answer_type == question.ANSWER_TYPE_MULTIPLE_SELECT:
            field = AdjudicatorFeedbackCheckboxSelectMultipleField(choices=question.choices_for_field)
        field.label = question.text
        if question.required:
            field.label += "*"
        field.required = self._enforce_required and question.required
        return field

    def _create_fields(self):
        """Creates dynamic fields in the form."""
        # Feedback questions defined for the tournament
        adj_min_score = self._tournament.pref('adj_min_score')
        adj_max_score = self._tournament.pref('adj_max_score')
        score_label = mark_safe("Overall score<br />(%s=lowest, %s=highest)" % (adj_min_score, adj_max_score))
        self.fields['score'] = forms.FloatField(min_value=adj_min_score, max_value=adj_max_score, label=score_label)

        for question in self._tournament.adj_feedback_questions.filter(**self.question_filter):
            self.fields[question.reference] = self._make_question_field(question)

        # Tournament password field, if applicable
        if self._use_tournament_password and self._tournament.pref('public_use_password'):
            self.fields['password'] = TournamentPasswordField(tournament=self._tournament)

    def save_adjudicatorfeedback(self, **kwargs):
        """Saves the question fields and returns the AdjudicatorFeedback.
        To be called by save() of child classes."""
        af = AdjudicatorFeedback(**kwargs)

        if self._confirm_on_submit:
            self.discard_all_existing(adjudicator=kwargs['adjudicator'],
                                      source_adjudicator=kwargs['source_adjudicator'],
                                      source_team=kwargs['source_team'])
            af.confirmed = True

        af.score = self.cleaned_data['score']
        af.save()

        for question in self._tournament.adj_feedback_questions.filter(**self.question_filter):
            if self.cleaned_data[question.reference] is not None:
                answer = question.answer_type_class(
                    feedback=af, question=question, answer=self.cleaned_data[question.reference])
                answer.save()

        return af

    def discard_all_existing(self, **kwargs):
        for fb in AdjudicatorFeedback.objects.filter(**kwargs):
            fb.discarded = True
            fb.save()


def make_feedback_form_class(source, tournament, *args, **kwargs):
    """Constructs a FeedbackForm class specific to the given source.
    'source' is the Adjudicator or Team who is giving feedback.
    'submission_fields' is a dict of fields that is passed directly as keyword
        arguments to Submission.
    'confirm_on_submit' is a bool, and indicates that this feedback should be
        as confirmed and all others discarded."""
    if isinstance(source, Adjudicator):
        return make_feedback_form_class_for_adj(source, tournament, *args, **kwargs)
    elif isinstance(source, Team):
        return make_feedback_form_class_for_team(source, tournament, *args, **kwargs)
    else:
        raise TypeError('source must be Adjudicator or Team: %r' % source)


def make_feedback_form_class_for_adj(source, tournament, submission_fields, confirm_on_submit=False,
                                     enforce_required=True, include_unreleased_draws=False):
    """Constructs a FeedbackForm class specific to the given source adjudicator.
    Parameters are as for make_feedback_form_class."""

    def adj_choice(adj, debate, pos):
        value = '%d-%d' % (debate.id, adj.id)
        display = '%s (%s, %s)' % (adj.name, debate.round.name, ADJUDICATOR_POSITION_NAMES[pos])
        return (value, display)

    debateadjs = DebateAdjudicator.objects.filter(
        debate__round__tournament=tournament, adjudicator=source,
        debate__round__seq__lte=tournament.current_round.seq,
        debate__round__stage=Round.STAGE_PRELIMINARY
    ).order_by('-debate__round__seq').prefetch_related(
        'debate__debateadjudicator_set__adjudicator'
    )

    if include_unreleased_draws:
        debateadjs = debateadjs.filter(debate__round__draw_status__in=[Round.STATUS_CONFIRMED, Round.STATUS_RELEASED])
    else:
        debateadjs = debateadjs.filter(debate__round__draw_status=Round.STATUS_RELEASED)

    choices = [(None, '-- Adjudicators --')]
    for debateadj in debateadjs:
        targets = expected_feedback_targets(debateadj, tournament.pref('feedback_paths'))
        for target, pos in targets:
            choices.append(adj_choice(target, debateadj.debate, pos))

    class FeedbackForm(BaseFeedbackForm):
        _tournament = tournament  # BaseFeedbackForm setting
        _use_tournament_password = True  # BaseFeedbackForm setting
        _confirm_on_submit = confirm_on_submit
        _enforce_required = enforce_required
        question_filter = dict(from_adj=True)

        target = RequiredTypedChoiceField(choices=choices, coerce=BaseFeedbackForm.coerce_target, label='Adjudicator this feedback is about')

        def save(self):
            """Saves the form and returns the AdjudicatorFeedback object."""
            debate, target = self.cleaned_data['target']
            sa = DebateAdjudicator.objects.get(adjudicator=source, debate=debate)
            kwargs = dict(adjudicator=target, source_adjudicator=sa, source_team=None)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm


def make_feedback_form_class_for_team(source, tournament, submission_fields, confirm_on_submit=False,
                                      enforce_required=True, include_unreleased_draws=False):
    """Constructs a FeedbackForm class specific to the given source team.
    Parameters are as for make_feedback_form_class."""

    def adj_choice(adj, debate, pos):
        value = '%d-%d' % (debate.id, adj.id)
        if tournament.pref('feedback_from_teams') == 'all-adjs':
            if pos == AdjudicatorAllocation.POSITION_ONLY:
                pos_text = ''
            else:
                pos_text = ' ' + ADJUDICATOR_POSITION_NAMES[pos]
        else:
            if pos == AdjudicatorAllocation.POSITION_CHAIR:
                pos_text = '—chair gave oral'
            elif pos == AdjudicatorAllocation.POSITION_PANELLIST:
                pos_text = '—chair rolled, this panellist gave oral'
            elif pos == AdjudicatorAllocation.POSITION_ONLY:
                pos_text = ''

        display = '{name} ({r}{pos})'.format(name=adj.name, r=debate.round.name, pos=pos_text)
        return (value, display)

    # Only include non-silent rounds for teams.
    debates = Debate.objects.filter(
        debateteam__team=source, round__silent=False,
        round__seq__lte=tournament.current_round.seq,
        round__stage=Round.STAGE_PRELIMINARY
    ).order_by('-round__seq').prefetch_related('debateadjudicator_set__adjudicator')
    if include_unreleased_draws:
        debates = debates.filter(round__draw_status__in=[Round.STATUS_CONFIRMED, Round.STATUS_RELEASED])
    else:
        debates = debates.filter(round__draw_status=Round.STATUS_RELEASED)

    choices = [(None, '-- Adjudicators --')]
    for debate in debates:
        if tournament.pref('feedback_from_teams') == 'all-adjs':
            das = debate.adjudicators.with_positions()
        else:
            das = debate.adjudicators.voting_with_positions()

        for adj, pos in das:
            choices.append(adj_choice(adj, debate, pos))

    class FeedbackForm(BaseFeedbackForm):
        _tournament = tournament  # BaseFeedbackForm setting
        _use_tournament_password = True  # BaseFeedbackForm setting
        _confirm_on_submit = confirm_on_submit
        _enforce_required = enforce_required
        question_filter = dict(from_team=True)

        target = RequiredTypedChoiceField(choices=choices, coerce=BaseFeedbackForm.coerce_target)

        def save(self):
            # Saves the form and returns the m.AdjudicatorFeedback object
            debate, target = self.cleaned_data['target']
            st = DebateTeam.objects.get(team=source, debate=debate)
            kwargs = dict(adjudicator=target, source_adjudicator=None, source_team=st)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm
