from django import forms
from django.utils.translation import ugettext as _

import debate.models as m
from results.result import BallotSet, ForfeitBallotSet

from collections import Counter
import itertools
import logging
logger = logging.getLogger(__name__)

class FormConstructionError(Exception):
    pass

# ==============================================================================
# Custom fields
# ==============================================================================

class BaseScoreField(forms.FloatField):
    def __init__(self, *args, **kwargs):
        """Takes an additional optional keyword argument: tournament_config,
        the Config object for the Tournament."""

        tournament_config = kwargs.pop('tournament_config')
        if tournament_config:
            min_value  = tournament_config.get(self.CONFIG_MIN_VALUE_FIELD, default=self.DEFAULT_MIN_VALUE)
            max_value  = tournament_config.get(self.CONFIG_MAX_VALUE_FIELD, default=self.DEFAULT_MAX_VALUE)
            step_value = tournament_config.get(self.CONFIG_STEP_VALUE_FIELD, default=self.DEFAULT_STEP_VALUE)
        else:
            min_value  = self.DEFAULT_MIN_VALUE
            max_value  = self.DEFAULT_MAX_VALUE
            step_value = self.DEFAULT_STEP_VALUE
        self.step_value = kwargs.get('step_value', step_value)

        kwargs.setdefault('min_value', min_value)
        kwargs.setdefault('max_value', max_value)

        # Overwrite the "step" attribute.
        # Note, this overrides everything, so it means you can't set the
        # 'step' attribute of the widget directly - you must use the
        # step_value keyword argument.
        widget = kwargs.get('widget', self.widget)
        if isinstance(widget, type):
            widget = widget()
        if isinstance(widget, forms.NumberInput):
            widget.attrs['step'] = self.step_value
        kwargs['widget'] = widget

        super(BaseScoreField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(BaseScoreField, self).validate(value)
        self.check_value(value)

    def check_value(self, value):
        if value:
            if value % self.step_value != 0:
                if self.step_value == 1:
                    msg = 'Please enter a whole number.'
                else:
                    msg = 'Please enter a multiple of %s.' % self.step_value
                raise forms.ValidationError(
                    _(msg), code='decimal'
                )


class SubstantiveScoreField(BaseScoreField):
    CONFIG_MIN_VALUE_FIELD  = 'score_min'
    CONFIG_MAX_VALUE_FIELD  = 'score_max'
    CONFIG_STEP_VALUE_FIELD = 'score_step'
    DEFAULT_MIN_VALUE = 68
    DEFAULT_MAX_VALUE = 82
    DEFAULT_STEP_VALUE = 1


class ReplyScoreField(BaseScoreField):
    CONFIG_MIN_VALUE_FIELD  = 'reply_score_min'
    CONFIG_MAX_VALUE_FIELD  = 'reply_score_max'
    CONFIG_STEP_VALUE_FIELD = 'reply_score_step'
    DEFAULT_MIN_VALUE = 34
    DEFAULT_MAX_VALUE = 41
    DEFAULT_STEP_VALUE = 0.5


class TournamentPasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'tournament' in kwargs:
            tournament = kwargs.pop('tournament')
            self.password = tournament.config.get('public_password')
        else:
            raise TypeError("'tournament' is a required keyword argument")
        if 'label' not in kwargs:
            kwargs['label'] = "Tournament password"
        super(TournamentPasswordField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TournamentPasswordField, self).clean(value)
        if value != self.password:
            raise forms.ValidationError(_("That password isn't correct."))
        return value

class MotionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%d. %s" % (obj.seq, obj.text)


# TODO: move to a more general forms.py? is used by breaking+feedback
class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)
