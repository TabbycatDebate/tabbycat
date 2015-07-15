from django import forms
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.utils.safestring import mark_safe

import debate.models as m
from debate.result import BallotSet, ForfeitBallotSet

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


class RequiredTypedChoiceField(forms.TypedChoiceField):
    def clean(self, value):
        value = super(RequiredTypedChoiceField, self).clean(value)
        if value == "None":
            raise forms.ValidationError(_("This field is required."))
        return value


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

class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)

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
        return m.AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR.join(value)

# ==============================================================================
# Result/ballot forms
# ==============================================================================

class BallotSetForm(forms.Form):
    """Form for data entry for a single ballot set. Responsible for presenting
    the part that looks like a ballot, i.e. speaker names and scores for each
    adjudicator. Not responsible for controls that submit the form or anything
    like that.
    """

    confirmed = forms.BooleanField(required=False)
    discarded = forms.BooleanField(required=False)

    debate_result_status = forms.ChoiceField(choices=m.Debate.STATUS_CHOICES)

    SIDES = ['aff', 'neg']
    _LONG_NAME = {'aff': 'affirmative', 'neg': 'negative'}

    def __init__(self, ballotsub, *args, **kwargs):
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.adjudicators = self.debate.adjudicators.list
        self.motions = self.debate.round.motion_set
        self.tournament = self.debate.round.tournament
        self.tconfig = self.tournament.config
        self.using_motions = self.tconfig.get('enable_motions')
        self.using_vetoes = self.tconfig.get('motion_vetoes_enabled')
        self.using_forfeits = self.tconfig.get('enable_forfeits')
        self.using_replies = self.tconfig.get('reply_scores_enabled')
        self.choosing_sides = self.tconfig.get('draw_side_allocations') == 'manual-ballot'

        self.forfeit_declared = False

        self.has_tournament_password = kwargs.pop('password', False) and self.tournament.config.get('public_use_password')

        super(BallotSetForm, self).__init__(*args, **kwargs)

        self.POSITIONS = self.tournament.POSITIONS
        self.LAST_SUBSTANTIVE_POSITION = self.tournament.LAST_SUBSTANTIVE_POSITION # also used in template
        self.REPLY_POSITION = self.tournament.REPLY_POSITION # also used in template

        self._create_fields()
        self._set_tab_indices()
        self.initial = self._initial_data()

    @property
    def SIDES_AND_POSITIONS(self):
        return itertools.product(self.SIDES, self.POSITIONS)

    # --------------------------------------------------------------------------
    # Field names and field convenience functions
    # --------------------------------------------------------------------------

    @staticmethod
    def _fieldname_motion_veto(side):
        return '%(side)s_motion_veto' % {'side': side}

    @staticmethod
    def _fieldname_speaker(side, pos):
        return '%(side)s_speaker_s%(pos)d' % {'side': side, 'pos': pos}

    @staticmethod
    def _fieldname_score(adj, side, pos):
        return '%(side)s_score_a%(adj)d_s%(pos)d' % {'adj': adj.id, 'side': side, 'pos': pos}

    def score_field(self, adj, side, pos):
        return self[self._fieldname_score(adj, side, pos)]

    # --------------------------------------------------------------------------
    # Form set-up
    # --------------------------------------------------------------------------

    def _create_fields(self):
        """Dynamically generate fields for this ballot:
         - password
         - choose_sides,         if sides need to be chosen by the user
         - motion,               if there is more than one motion
         - aff/neg_motion_veto,  if motion vetoes are being noted, one for each team
         - aff/neg_speaker_s#,   one for each speaker
         - aff/neg_score_a#_s#,  one for each score
        """

        dts = self.debate.debateteam_set.all()

        # 1. Tournament password field
        if self.has_tournament_password:
            self.fields['password'] = TournamentPasswordField(tournament=self.tournament)

        # 2. Choose sides field
        if self.choosing_sides:
            if len(dts) != 2:
                raise FormConstructionError('Whoops! There are %d teams in this debate, was expecting 2.' % len(dts))
            teams = self.debate.teams
            side_choices = [
                (None, "---------"),
                (str(teams[0].id) + "," + str(teams[1].id), "%s affirmed, %s negated" % (teams[0].short_name, teams[1].short_name)),
                (str(teams[1].id) + "," + str(teams[0].id), "%s affirmed, %s negated" % (teams[1].short_name, teams[0].short_name))
            ]
            self.fields['choose_sides'] = forms.TypedChoiceField(
                choices=side_choices, coerce=lambda x: tuple(m.Team.objects.get(id=int(v)) for v in x.split(","))
            )
            for team in self.debate.teams:
                self.fields['team_%d' % team.id] = forms.ModelChoiceField(queryset=team.speakers, required=False)

        # 3. Motions fields
        if self.using_motions:
            self.fields['motion'] = forms.ModelChoiceField(queryset=self.motions, required=True)
            for side in self.SIDES:
                self.fields[self._fieldname_motion_veto(side)] = forms.ModelChoiceField(queryset=self.motions, required=False)

        # 4. Speaker fields
        for side, pos in self.SIDES_AND_POSITIONS:

            # 4(a). Speaker identity
            if self.choosing_sides:
                queryset = m.Speaker.objects.filter(team__in=self.debate.teams)
            else:
                queryset = self.debate.get_team(side).speakers
            self.fields[self._fieldname_speaker(side, pos)] = forms.ModelChoiceField(queryset=queryset)

            # 4(b). Speaker scores
            ScoreField = ReplyScoreField if (pos == self.REPLY_POSITION) else SubstantiveScoreField
            for adj in self.adjudicators:
                self.fields[self._fieldname_score(adj, side, pos)] = ScoreField(
                        widget=forms.NumberInput(attrs={'class': 'required number'}),
                        tournament_config=self.tconfig)

        # 5. If forfeits are enabled, don't require some fields and add the forfeit field
        if self.using_forfeits:
            for side, pos in self.SIDES_AND_POSITIONS:
                self.fields[self._fieldname_score(adj, side, pos)].required = False
                self.fields[self._fieldname_speaker(side, pos)].required = False
            self.fields['motion'].required = False
            CHOICES = (('aff_forfeit', 'Forfeit by the Affirmative',), ('neg_forfeit', 'Forfeit by the Negative',))
            self.fields['forfeits'] = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=False)

    def _initial_data(self):
        """Generates dictionary of initial form data."""

        ballotset = BallotSet(self.ballotsub)
        initial = {'debate_result_status': self.debate.result_status,
                'confirmed': ballotset.confirmed, 'discarded': ballotset.discarded}

        # HACK: Check here to see if self.ballotsub has been saved -- if it's not,
        # then it's a new ballot set, and choose_sides should not be populated
        # with an initial value. Fix when models support a proper "no side
        # assigned" state (it currently doesn't).
        if self.choosing_sides and self.ballotsub.pk is not None:
            try:
                initial['choose_sides'] = str(self.debate.aff_team.id) + "," + str(self.debate.neg_team.id)
            except m.DebateTeam.DoesNotExist:
                pass

        # Generally, initialise the motion to what is currently in the database.
        # But if there is only one motion and no motion is currently stored in
        # the database for this round, then default to the only motion there is.
        if self.using_motions:
            if not ballotset.motion and self.motions.count() == 1:
                initial['motion'] = self.motions.get()
            else:
                initial['motion'] = ballotset.motion
            for side in self.SIDES:
                initial[self._fieldname_motion_veto(side)] = ballotset.get_motion_veto(side)

        for side, pos in self.SIDES_AND_POSITIONS:
            speaker = ballotset.get_speaker(side, pos)
            if speaker:
                initial[self._fieldname_speaker(side, pos)] = speaker.pk
                for adj in self.adjudicators:
                    score = ballotset.get_score(adj, side, pos)
                    initial[self._fieldname_score(adj, side, pos)] = score

        return initial

    def _set_tab_indices(self):
        """Sets all the tab indices in the form."""
        # make a list for field names, then set them all at the end
        order = list()

        if 'choose_sides' in self.fields:
            order.append('choose_sides')

        if self.motions.count() > 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.SIDES)

        for side, pos in self.SIDES_AND_POSITIONS:
            order.append(self._fieldname_speaker(side, pos))

        for adj, side, pos in itertools.product(self.adjudicators, self.SIDES, self.POSITIONS):
            order.append(self._fieldname_score(adj, side, pos))

        if 'password' in self.fields:
            order.append('password')
        if 'forfeits' in self.fields:
            order.append('forfeits')

        order.extend(['discarded', 'confirmed', 'debate_result_status'])

        if self.motions.count() <= 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.SIDES)

        # now, set
        for i, name in enumerate(order, start=1):
            try:
                self.fields[name].widget.attrs['tabindex'] = i
            except KeyError as e:
                logger.warning(e.message)

        self.nexttabindex = i + 1 # for other UI elements in the tempate

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean(self):
        cleaned_data = super(BallotSetForm, self).clean()
        errors = list()

        if cleaned_data.get('forfeits') in ["aff_forfeit", "neg_forfeit"]:
            self.forfeit_declared = True

        if cleaned_data.get('discarded') and cleaned_data.get('confirmed'):
            for field in ('discarded', 'confirmed'):
                self.add_error(field, forms.ValidationError(
                    _("The ballot set can't be both discarded and confirmed."),
                    code='discard_confirm'
                ))

        if cleaned_data.get('debate_result_status') == m.Debate.STATUS_CONFIRMED and not cleaned_data.get('confirmed') and self.debate.confirmed_ballot is None:
            self.add_error('debate_result_status', forms.ValidationError(
                _("The debate status can't be confirmed unless one of the ballot sets is confirmed."),
                code='status_confirm'
            ))

        if not self.forfeit_declared:
            for adj in self.adjudicators:
                # Check that it was not a draw.
                try:
                    totals = [sum(cleaned_data[self._fieldname_score(adj, side, pos)] for pos in self.POSITIONS) for side in self.SIDES]
                except KeyError as e:
                    logger.warning("Field %s not found", str(e))
                if totals[0] == totals[1]:
                    self.add_error(None, forms.ValidationError(
                        _("The total scores for the teams are the same (i.e. a draw) for adjudicator %(adj)s (%(adj_ins)s)"),
                        params={'adj': adj.name, 'adj_ins': adj.institution.code}, code='draw'
                    ))


            # Pull team info again, in case it's changed since the form was loaded.
            if self.choosing_sides:
                teams = cleaned_data.get('choose_sides', [None] * len(self.SIDES))
            else:
                teams = [self.debate.get_team(side) for side in self.SIDES]
            if None in teams:
                logger.warning("Team identities not found")

            for side, team in zip(self.SIDES, teams):

                speaker_counts = Counter()
                for pos in xrange(1, self.LAST_SUBSTANTIVE_POSITION + 1):
                    speaker = self.cleaned_data.get(self._fieldname_speaker(side, pos))
                    if speaker is None:
                        logger.warning("Field '%s' not found", self._fieldname_speaker(side, pos))
                        continue

                    # The speaker must be on the relevant team.
                    if team is not None and speaker not in team.speakers:
                        self.add_error(self._fieldname_speaker(side, pos), forms.ValidationError(
                            _("The speaker %(speaker)s doesn't appear to be on team %(team)s."),
                            params={'speaker': speaker.name, 'team': team.short_name}, code='speaker_wrongteam'
                            ))
                    speaker_counts[speaker] += 1

                # The substantive speakers must be unique.
                for speaker, count in speaker_counts.iteritems():
                    if count > 1:
                        self.add_error(None, forms.ValidationError(
                            _("The speaker %(speaker)s appears to have given multiple (%(count)d) substantive speeches for the %(side)s team."),
                            params={'speaker': speaker.name, 'side': self._LONG_NAME[side], 'count': count}, code='speaker_repeat'
                        ))

                if self.using_replies:
                    reply_speaker = cleaned_data.get(self._fieldname_speaker(side, self.REPLY_POSITION))
                    last_speaker = cleaned_data.get(self._fieldname_speaker(side, self.LAST_SUBSTANTIVE_POSITION))

                    # The third speaker can't give the reply.
                    if reply_speaker == last_speaker and reply_speaker is not None:
                        self.add_error(self._fieldname_speaker(side, self.REPLY_POSITION), forms.ValidationError(
                            _("The last substantive speaker and reply speaker for the %(side)s team can't be the same."),
                            params={'side': self._LONG_NAME[side]}, code='reply_speaker_consecutive'
                            ))

                    # The reply speaker must have given a substantive speech.
                    if speaker_counts[reply_speaker] == 0:
                        self.add_error(self._fieldname_speaker(side, self.REPLY_POSITION), forms.ValidationError(
                            _("The reply speaker for the %(side)s team did not give a substantive speech."),
                            params={'side': self._LONG_NAME[side]}, code='reply_speaker_not_repeat'
                        ))

        return cleaned_data

    def save(self):

        # 1. Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballotsub and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        # 2. Check if there was a forfeit
        if self.using_forfeits and self.forfeit_declared:
            if self.cleaned_data['forfeits'] == "aff_forfeit":
                forfeiter = self.debate.aff_dt
            if self.cleaned_data['forfeits'] == "neg_forfeit":
                forfeiter = self.debate.neg_dt
            ballotset = ForfeitBallotSet(self.ballotsub, forfeiter)
        else:
            ballotset = BallotSet(self.ballotsub)

        # 3. Save the sides
        if self.choosing_sides:
            ballotset.set_sides(*self.cleaned_data['choose_sides'])

        # 4. Save motions
        if self.using_motions:
            ballotset.motion = self.cleaned_data['motion']

        if self.using_vetoes:
            for side in self.SIDES:
                motion_veto = self.cleaned_data[self._fieldname_motion_veto(side)]
                ballotset.set_motion_veto(side, motion_veto)

        # 5. Save speaker fields
        if not self.forfeit_declared:
            print "saving speaker fields"
            for side, pos in self.SIDES_AND_POSITIONS:
                speaker = self.cleaned_data[self._fieldname_speaker(side, pos)]
                ballotset.set_speaker(side, pos, speaker)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self._fieldname_score(adj, side, pos)]
                    ballotset.set_score(adj, side, pos, score)

        # 6. Save status fields
        ballotset.discarded = self.cleaned_data['discarded']
        ballotset.confirmed = self.cleaned_data['confirmed']
        ballotset.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def fake_speaker_selects(self):
        for team in self.debate.teams:
            yield self['team_%d' % team.id]

    def adj_iter(self):
        form = self # provide access in inner classes

        class Position(object):
            def __init__(self, adj, pos):
                self.adj = adj
                self.pos = pos

            @property
            def name(self):
                return (self.pos == form.REPLY_POSITION) and "Reply" or str(self.pos)

            def __unicode__(self):
                return unicode(self.name)

            def aff_speaker(self):
                return form[form._fieldname_speaker('aff', self.pos)]

            def neg_speaker(self):
                return form[form._fieldname_speaker('neg', self.pos)]

            def _scores(self, side):
                for adj in form.adjudicators:
                    yield form.score_field(adj, side, self.pos)

            def aff_score(self):
                return str(form.score_field(self.adj, 'aff', self.pos))

            def aff_score_errors(self):
                return str(form.score_field(self.adj, 'aff', self.pos).errors)

            def neg_score(self):
                return str(form.score_field(self.adj, 'neg', self.pos))

            def neg_score_errors(self):
                return str(form.score_field(self.adj, 'neg', self.pos).errors)

        class AdjudicatorWrapper(object):
            def __init__(self, adj):
                self.adj = adj

            def position_iter(self):
                for i in form.POSITIONS:
                    yield Position(self.adj, i)


        for adj in self.adjudicators:
            yield AdjudicatorWrapper(adj)


class DebateManagementForm(forms.Form):
    """ NOT CURRENTLY USED
    Traditionally, a Django FormSet has a ManagementForm to keep track of the
    forms on the page. In a debate result, there are some fields the relate to the
    debate as a whole, not an individual ballot. This form is responsible for those
    fields, and is always part of a DebateResultFormSet."""

    result_status = forms.ChoiceField(choices=m.Debate.STATUS_CHOICES)

    def __init__(self, debate, *args, **kwargs):
        self.debate = debate

        super(DebateManagementForm, self).__init__(*args, **kwargs)

        self.initial['result_status'] = self.debate.result_status

        # Generate the confirmed ballot field
        self.fields['confirmed_ballot'] = forms.ModelChoiceField(
            queryset = self.debate.ballotsubmission_set,
            required = False)
        self.initial['confirmed_ballot'] = self.debate.confirmed_ballot

    def save(self):
        # Unconfirm the old ballot
        # (Technically, we could rely on BallotSubmission.save() to do this
        # for us, but it's better to be explicit than rely on a backup check.)
        old_confirmed_ballot = self.debate.confirmed_ballot
        old_confirmed_ballot.confirmed = False
        old_confirmed_ballot.save()

        # Confirm the new ballot
        new_confirmed_ballot = self.cleaned_data['confirmed_ballot']
        new_confirmed_ballot.confirmed = True
        new_confirmed_ballot.save()

        # Update the debate status
        # TODO catch validation errors
        self.debate.result_status = self.cleaned_data['result_status']
        self.debate.save()

class DebateResultFormSet(object):
    """ NOT CURRENTLY USED
    A manager for the various forms that comprise a debate result form.

    This should only be used with tab room interfaces. The public should never
    see anything remotely resembling this form set.

    In many ways, this is similar to FormSet. But it adds too much functionality
    specific to debate results, including managing relationships between forms,
    and uses too little of BaseFormSet's actual functionality, to be worth
    inheriting from BaseFormSet. Maybe we'll eventually change this."""

    # TODO Add a ManagementForm to this, if we ever want to add/delete forms using JavaScript

    def __init__(self, debate, data=None, *args, **kwargs):
        """Dynamically generate the ballot set forms for this debate.
        Basically we do this by initializing the data of the formset."""

        self.debate_management_form = DebateManagementForm(debate)
        self.ballotset_forms = list()

        for ballot in debate.ballotsubmission_set.all():
            form = BallotSetForm(ballot)
            self.ballotset_forms.append(form)

    def save(self):
        pass


# ==============================================================================
# Break eligbility form
# ==============================================================================

class BreakEligibilityForm(forms.Form):
    """Sets which teams are eligible for the break."""

    def __init__(self, tournament, *args, **kwargs):
        super(BreakEligibilityForm, self).__init__(*args, **kwargs)
        self.tournament = tournament
        self._create_and_initialise_fields()

    @staticmethod
    def _fieldname_eligibility(team):
        return 'eligibility_%(team)d' % {'team': team.id}

    def _create_and_initialise_fields(self):
        """Dynamically generate fields for this ballot, one
        ModelMultipleChoiceField for each Team."""
        for team in self.tournament.team_set.all():
            self.fields[self._fieldname_eligibility(team)] = forms.ModelMultipleChoiceField(
                    queryset=self.tournament.breakcategory_set.all(), widget=forms.CheckboxSelectMultiple,
                    required=False)
            self.initial[self._fieldname_eligibility(team)] = team.break_categories.all()

    def save(self):
        for team in self.tournament.team_set.all():
            team.break_categories = self.cleaned_data[self._fieldname_eligibility(team)]
            team.save()

    def team_iter(self):
        form = self # provide access to inner classes

        class TeamWrapper(object):
            def __init__(self, team):
                self.team = team
                self.eligibility = form[form._fieldname_eligibility(self.team)]

        for team in self.tournament.team_set.all():
            yield TeamWrapper(team)


# ==============================================================================
# Feedback forms
# ==============================================================================

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
        af = m.AdjudicatorFeedback(**kwargs)

        if self._confirm_on_submit:
            self.discard_all_existing(adjudicator=kwargs['adjudicator'],
                    source_adjudicator=kwargs['source_adjudicator'],
                    source_team=kwargs['source_team'])
            af.confirmed = True

        af.score = self.cleaned_data['score']
        af.full_clean()
        af.save()

        for question in self.tournament.adj_feedback_questions.filter(**self.question_filter):
            if self.cleaned_data[question.reference] is not None:
                answer = question.answer_type_class(feedback=af, question=question,
                        answer=self.cleaned_data[question.reference])
                answer.full_clean()
                answer.save()

        return af

    def discard_all_existing(self, **kwargs):
        for fb in m.AdjudicatorFeedback.objects.filter(**kwargs):
            fb.discarded = True
            fb.save()

def make_feedback_form_class(source, *args, **kwargs):
    """Constructs a FeedbackForm class specific to the given source.
    'source' is the Adjudicator or Team who is giving feedback.
    'submission_fields' is a dict of fields that is passed directly as keyword
        arguments to Submission.
    'confirm_on_submit' is a bool, and indicates that this feedback should be
        as confirmed and all others discarded."""
    if isinstance(source, m.Adjudicator):
        return make_feedback_form_class_for_adj(source, *args, **kwargs)
    elif isinstance(source, m.Team):
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
        return m.DebateAdjudicator.objects.get(id=int(value))

    debate_filter = dict(debateadjudicator__adjudicator=source,
            round__draw_status=m.Round.STATUS_RELEASED)
    if not source.tournament.config.get('panellist_feedback_enabled'): # then include only debates for which this adj was the chair
        debate_filter['debateadjudicator__type'] = m.DebateAdjudicator.TYPE_CHAIR
    debates = m.Debate.objects.filter(**debate_filter)

    choices = [(None, '-- Adjudicators --')]
    choices.extend(adj_choice(da) for da in     # for an adjudicator, find every adjudicator on their panel except them.
            m.DebateAdjudicator.objects.filter(debate__in=debates).exclude(adjudicator=source).select_related('debate').order_by('-debate__round__seq'))

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
            sa = m.DebateAdjudicator.objects.get(adjudicator=source, debate=da.debate)
            kwargs = dict(adjudicator=da.adjudicator, source_adjudicator=sa, source_team=None)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm

def make_feedback_form_class_for_team(source, submission_fields, confirm_on_submit=False, enforce_required=True):
    """Constructs a FeedbackForm class specific to the given source team.
    Parameters are as for make_feedback_form_class."""

    # Only include non-silent rounds for teams.
    debates = m.Debate.objects.filter(debateteam__team=source, round__silent=False,
        round__draw_status=m.Round.STATUS_RELEASED).order_by('-round__seq')

    choices = [(None, '-- Adjudicators --')]
    for debate in debates:
        try:
            chair = m.DebateAdjudicator.objects.get(debate=debate, type=m.DebateAdjudicator.TYPE_CHAIR)
        except m.DebateAdjudicator.DoesNotExist:
            continue
        panel = m.DebateAdjudicator.objects.filter(debate=debate, type=m.DebateAdjudicator.TYPE_PANEL)
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
        return m.DebateAdjudicator.objects.get(id=int(value))

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
            st = m.DebateTeam.objects.get(team=source, debate=da.debate)
            kwargs = dict(adjudicator=da.adjudicator, source_adjudicator=None, source_team=st)
            kwargs.update(submission_fields)
            return self.save_adjudicatorfeedback(**kwargs)

    return FeedbackForm


def test():
    return make_results_form_class(m.Debate.objects.get(pk=1))

