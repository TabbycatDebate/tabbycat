from django import forms
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from debate.models import SpeakerScoreByAdj, Debate, Motion, Round, Team, Adjudicator
from debate.models import DebateTeam, DebateTeamMotionPreference, DebateAdjudicator, AdjudicatorFeedback
from debate.models import ActionLog
from debate.result import BallotSet, ForfeitBallotSet

from collections import Counter
import itertools
import logging
logger = logging.getLogger(__name__)

class FormConstructionError(Exception):
    pass

class MalformedFormError(forms.ValidationError):
    def __init__(self):
        forms.ValidationError.__init__(self, "The form data seems malformed, please try again.")

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
        value = super(forms.TypedChoiceField, self).clean(value)
        if value == "None":
            raise forms.ValidationError(_("This field is required."))
        return value


class CustomNullBooleanSelect(forms.NullBooleanSelect):

    def __init__(self, attrs=None):
        choices = (('1', ugettext_lazy('Not sure')),
                   ('2', ugettext_lazy('Yes')),
                   ('3', ugettext_lazy('No')))
        # skip the NullBooleanSelect constructor
        super(forms.NullBooleanSelect, self).__init__(attrs, choices)


# ==============================================================================
# Result/ballot forms
# ==============================================================================

class BallotSetForm(forms.Form):
    """Form for data entry for a single set of ballots. Responsible for
    presenting the part that looks like a ballot, i.e. speaker names and scores
    for each adjudicator. Not responsible for controls that submit the form or
    anything like that.
    """

    confirmed = forms.BooleanField(required=False)
    discarded = forms.BooleanField(required=False)

    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

    SIDES = ['aff', 'neg']
    _LONG_NAME = {'aff': 'affirmative', 'neg': 'negative'}

    def __init__(self, ballots, *args, **kwargs):
        """Dynamically generate fields for this ballot:
         - password
         - choose_sides,    if sides need to be chosen by the user
         - motion,          if there is more than one motion
         - motion_veto_t#,  if motion vetoes are being noted, one for each team
         - speaker t#_s#,   one for each speaker
         - score_a#_t#_s#,  one for each score
        """

        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicators = self.debate.adjudicators.list
        self.motions = self.debate.round.motion_set
        self.tournament = self.debate.round.tournament
        self.tconfig = self.tournament.config
        self.using_motions = self.tconfig.get('enable_motions')
        self.using_forfeits = self.tconfig.get('enable_forfeits')
        self.using_replies = self.tconfig.get('reply_scores_enabled')
        self.choosing_sides = self.tconfig.get('draw_side_allocations') == 'manual-ballot'

        self.forfeit_declared = False

        self.has_tournament_password = kwargs.pop('password', False) and tournament.config.get('public_use_password')

        super(BallotSetForm, self).__init__(*args, **kwargs)

        self.POSITIONS = self.tournament.POSITIONS
        self.LAST_SUBSTANTIVE_POSITION = self.tournament.LAST_SUBSTANTIVE_POSITION
        self.REPLY_POSITION = self.tournament.REPLY_POSITION

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
        """Creates dynamic fields in the form."""
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
                choices=side_choices, coerce=lambda x: tuple(Team.objects.get(id=int(v)) for v in x.split(","))
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
            try:
                queryset = self.debate.get_team(side).speakers
            except (AttributeError, Team.DoesNotExist):
                queryset = Speaker.objects.none() # if sides not chosen
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
            self.fields['motion'].required = False
            CHOICES = (('aff_forfeit', 'Forfeit by the Affirmative',), ('neg_forfeit', 'Forfeit by the Negative',))
            self.fields['forfeits'] = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=False)

    def _initial_data(self):
        """Generates dictionary of initial form data."""

        bs = BallotSet(self.ballots)
        initial = {'debate_result_status': self.debate.result_status,
                'confirmed': bs.confirmed, 'discarded': bs.discarded}

        if self.choosing_sides:
            try:
                initial['choose_sides'] = str(self.debate.aff_team.id) + "," + str(self.debate.neg_team.id)
            except DebateTeam.DoesNotExist:
                pass

        # Generally, initialise the motion to what is currently in the database.
        # But if there is only one motion and no motion is currently stored in
        # the database for this round, then default to the only motion there is.
        if self.using_motions:
            if not bs.motion and self.motions.count() == 1:
                initial['motion'] = self.motions.get()
            else:
                initial['motion'] = bs.motion
            for side in self.SIDES:
                initial[self._fieldname_motion_veto(side)] = bs.get_motion_veto(side)

        for side, pos in self.SIDES_AND_POSITIONS:
            speaker = bs.get_speaker(side, pos)
            if speaker:
                initial[self._fieldname_speaker(side, pos)] = speaker.pk
                for adj in self.adjudicators:
                    score = bs.get_score(adj, side, pos)
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
            order.append(self._fieldname_score(self.adjudicators[0], side, pos))

        for adj, side, pos in itertools.product(self.adjudicators[1:], self.SIDES, self.POSITIONS):
            order.append(self._fieldname_score(adj, side, pos))

        if 'password' in self.fields:
            order.append('password')
        if 'forfeits' in self.fields:
            order.append('forfeits')

        order.extend(['discarded', 'confirmed', 'debate_result_status'])

        if self.motions.count() <= 1:
            order.extend(['motion', 'aff_motion_veto', 'neg_motion_veto'])

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

        if 'forfeits' in cleaned_data:
            if cleaned_data['forfeits'] in ["aff_forfeit", "neg_forfeit"]:
                self.forfeit_declared = True

        # TODO this should go up to the BallotSubmission.full_clean() method.
        # Not sure how to structure this.
        # For now just implement the same checks here.
        if cleaned_data['discarded'] and cleaned_data['confirmed']:
            errors.append(forms.ValidationError(
                _("The ballot set can't be both discarded and confirmed."),
                code='discard_confirm'
            ))
        if cleaned_data['debate_result_status'] == Debate.STATUS_CONFIRMED and not cleaned_data['confirmed'] and self.debate.confirmed_ballot is None:
            errors.append(forms.ValidationError(
                _("The debate status can't be confirmed unless one of the ballot sets is confirmed."),
                code='status_confirm'
            ))
        # end TODO

        if not self.forfeit_declared:
            for adj in self.adjudicators:
                # Check that it was not a draw.
                try:
                    totals = [sum(cleaned_data[self._fieldname_score(adj, side, pos)] for pos in self.POSITIONS) for side in self.SIDES]
                except KeyError:
                    logger.error("Field '%s' not found", self._fieldname_score(adj, side, pos))
                    raise MalformedFormError
                if totals[0] == totals[1]:
                    errors.append(forms.ValidationError(
                        _('The total scores for the teams are the same (i.e. a draw) for adjudicator %(adj)s (%(adj_ins)s)'),
                        params={'adj': adj.name, 'adj_ins': adj.institution.code}, code='draw'
                    ))

            for i, side in enumerate(self.SIDES):
                # Pull team speakers info again, in case it's changed since the form was loaded.
                team = self.cleaned_data['choose_sides'][i] if self.choosing_sides else self.debate.get_team(side)
                # The three substantive speaker fields must be unique.
                speakers = Counter()
                for pos in xrange(1, self.LAST_SUBSTANTIVE_POSITION + 1):
                    try:
                        speaker = cleaned_data[self._fieldname_speaker(side, pos)]
                    except KeyError:
                        logger.error("Field '%s' not found", self._fieldname_speaker(side, pos))
                        raise MalformedFormError
                    if speaker not in team.speakers:
                        errors.append(forms.ValidationError(
                            _('The speaker %(speaker)s doesn\'t appear to be on team %(team)s.'),
                            params={'speaker': speaker.name, 'team': team.short_name}, code='speaker_wrongteam'
                        ))
                    speakers[speaker] += 1
                for speaker, count in speakers.iteritems():
                    if count > 1:
                        errors.append(forms.ValidationError(
                            _('The speaker %(speaker)s appears to have given multiple (%(count)d) substantive speeches for the %(side)s team.'),
                            params={'speaker': speaker.name, 'side': self._LONG_NAME[side], 'count': count}, code='speaker_repeat'
                        ))

                # The third speaker can't give the reply.
                if self.using_replies:
                    try:
                        reply_speaker_error = cleaned_data[self._fieldname_speaker(side, self.LAST_SUBSTANTIVE_POSITION)] \
                                == cleaned_data[self._fieldname_speaker(side, self.REPLY_POSITION)]
                    except KeyError:
                        raise MalformedFormError
                    if reply_speaker_error:
                        errors.append(forms.ValidationError(
                            _('The last substantive speaker and reply speaker for the %(side)s team are the same.'),
                            params={'side': self._LONG_NAME[side]}, code='reply_speaker'
                        ))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def save(self):

        # 1. Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballots and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        # 2. Check if there was a forfeit
        if self.using_forfeits and self.forfeit_declared:
            if self.cleaned_data['forfeits'] == "aff_forfeit":
                forfeiter = self.debate.aff_dt
            if self.cleaned_data['forfeits'] == "neg_forfeit":
                forfeiter = self.debate.neg_dt
            bs = ForfeitBallotSet(self.ballots, forfeiter)
        else:
            bs = BallotSet(self.ballots)

        # 3. Save the sides
        if self.choosing_sides:
            bs.set_sides(*self.cleaned_data['choose_sides'])

        # 4. Save motions
        if self.using_motions:
            bs.motion = self.cleaned_data['motion']
            for side in self.SIDES:
                motion_veto = self.cleaned_data[self._fieldname_motion_veto(side)]
                bs.set_motion_veto(side, motion_veto)

        # 5. Save speaker fields
        if not self.forfeit_declared:
            for side, pos in self.SIDES_AND_POSITIONS:
                speaker = self.cleaned_data[self._fieldname_speaker(side, pos)]
                bs.set_speaker(side, pos, speaker)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self._fieldname_score(adj, side, pos)]
                    bs.set_score(adj, side, pos, score)

        # 6. Save status fields
        bs.discarded = self.cleaned_data['discarded']
        bs.confirmed = self.cleaned_data['confirmed']
        bs.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def team_ids(self):
        for team in self.debate.teams:
            yield team.id

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

    result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

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
# Feedback forms
# ==============================================================================

def make_feedback_form_class_for_tabroom(adjudicator, submission_fields, released_only=False):
    """adjudicator is an Adjudicator.
    submission_fields is a dict of fields for Submission.
    released_only is a boolean."""

    if released_only:
        das = DebateAdjudicator.objects.filter(adjudicator = adjudicator,
            debate__round__draw_status = Round.STATUS_RELEASED)
    else:
        das = DebateAdjudicator.objects.filter(adjudicator = adjudicator)

    debates = [da.debate for da in das]

    def adj_choice(da):
        return (
            'A:%d' % da.id,
            '%s (R%d, %s)' % (da.adjudicator.name, da.debate.round.seq,
                           da.get_type_display())
        )

    adj_choices = [(None, '-- Adjudicators --')]
    adj_choices.extend ([
        adj_choice(da) for da in DebateAdjudicator.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate') if da.adjudicator != adjudicator
    ])

    # Get rid of the heading if there aren't any adjudicators
    if len(adj_choices) == 1: adj_choices = []

    def team_choice(dt):
        return (
            'T:%d' % dt.id,
            '%s (%d)' % (dt.team.short_name, dt.debate.round.seq)
        )

    team_choices = [(None, '-- Teams --')]
    team_choices.extend([
        team_choice(dt) for dt in DebateTeam.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate')
    ])

    choices = adj_choices + team_choices

    def coerce(value):
        obj_type, id = value.split(':')
        id = int(id)

        if obj_type.strip() == 'A':
            return DebateAdjudicator.objects.get(id=id)
        if obj_type.strip() == 'T':
            return DebateTeam.objects.get(id=id)

    tournament = adjudicator.tournament

    class FeedbackForm(forms.Form):
        source = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        agree_with_decision = forms.NullBooleanField(widget=CustomNullBooleanSelect, label="Did you agree with their decision?", required=False)

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            source = self.cleaned_data['source']
            source = coerce(source) # Bug in Django 1.6.5

            if isinstance(source, DebateAdjudicator):
                sa = source
            else:
                sa = None
            if isinstance(source, DebateTeam):
                st = source
            else:
                st = None

            # Discard existing feedbacks
            for fb in AdjudicatorFeedback.objects.filter(adjudicator=adjudicator,
                    source_adjudicator=sa, source_team=st):
                fb.discarded = True
                fb.save()

            # Save the new one
            af = AdjudicatorFeedback(
                adjudicator       =adjudicator,
                source_adjudicator=sa,
                source_team       =st,
                confirmed         =True, # assume confirmed on every submission
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.agree_with_decision = self.cleaned_data['agree_with_decision']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm

def make_feedback_form_class_for_public_adj(source, submission_fields, include_panellists=True):

    kwargs = dict()
    kwargs['debate__round__draw_status'] = Round.STATUS_RELEASED

    def adj_choice(da):
        return (
            da.id,
            '%s (R%d, %s)' % (da.adjudicator.name, da.debate.round.seq,
                           da.get_type_display())
        )
    choices = [(None, '-- Adjudicators --')]

    if not include_panellists:
        # Include only debates for which this adj was the chair.
        kwargs['type'] = DebateAdjudicator.TYPE_CHAIR

    debates = [da.debate for da in DebateAdjudicator.objects.filter(
        adjudicator=source, **kwargs).select_related('debate')]

    # For an adjudicator, find every adjudicator on their panel except them.
    choices.extend([
        adj_choice(da) for da in DebateAdjudicator.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate').order_by('-debate__round') if da.adjudicator != source
    ])

    def coerce(value):
        value = int(value)
        return DebateAdjudicator.objects.get(id=value)

    tournament = source.tournament

    class FeedbackForm(forms.Form):
        debate_adjudicator = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        agree_with_decision = forms.NullBooleanField(widget=CustomNullBooleanSelect, label="Did you agree with their decision?", required=False)

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def __init__(self, *args, **kwargs):
            super(FeedbackForm, self).__init__(*args, **kwargs)
            if tournament.config.get('public_use_password'):
                self.fields['password'] = TournamentPasswordField(tournament=tournament)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            da = self.cleaned_data['debate_adjudicator']
            da = coerce(da) # Bug in Django 1.6.5

            sa = DebateAdjudicator.objects.get(adjudicator=source, debate=da.debate)

            af = AdjudicatorFeedback(
                adjudicator       =da.adjudicator,
                source_adjudicator=sa,
                source_team       =None,
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.agree_with_decision = self.cleaned_data['agree_with_decision']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm

def make_feedback_form_class_for_public_team(source, submission_fields, include_panellists=True):
    """source is an Adjudicator or Team.
    submission_fields is a dict of fields for Submission.
    released_only is a boolean."""

    choices = [(None, '-- Adjudicators --')]

    # Only include non-silent rounds for teams.
    debates = [dt.debate for dt in DebateTeam.objects.filter(
        team=source, debate__round__silent=False,
        debate__round__draw_status=Round.STATUS_RELEASED).select_related('debate').order_by('-debate__round__seq')]

    for debate in debates:
        try:
            chair = DebateAdjudicator.objects.get(debate=debate, type=DebateAdjudicator.TYPE_CHAIR)
        except DebateAdjudicator.DoesNotExist:
            continue
        panel = DebateAdjudicator.objects.filter(debate=debate, type=DebateAdjudicator.TYPE_PANEL)
        if panel.exists():
            choices.append((chair.id, '{name} (R{r} - chair gave oral)'.format(
                name=chair.adjudicator.name, r=debate.round.seq)))
            for da in panel:
                choices.append((da.id, '{name} (R{r} - chair rolled, this panellist gave oral)'.format(
                    name=da.adjudicator.name, r=debate.round.seq)))
        else:
            choices.append((chair.id, '{name} (R{r})'.format(
                name=chair.adjudicator.name, r=debate.round.seq)))

    def coerce(value):
        value = int(value)
        return DebateAdjudicator.objects.get(id=value)

    tournament = source.tournament

    class FeedbackForm(forms.Form):
        debate_adjudicator = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        agree_with_decision = forms.NullBooleanField(widget=CustomNullBooleanSelect, label="Did you agree with their decision?", required=False)

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def __init__(self, *args, **kwargs):
            super(FeedbackForm, self).__init__(*args, **kwargs)
            if tournament.config.get('public_use_password'):
                self.fields['password'] = TournamentPasswordField(tournament=tournament)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            da = self.cleaned_data['debate_adjudicator']
            da = coerce(da) # Bug in Django 1.6.5

            st = DebateTeam.objects.get(team=source, debate=da.debate)

            af = AdjudicatorFeedback(
                adjudicator       =da.adjudicator,
                source_adjudicator=None,
                source_team       =st,
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.agree_with_decision = self.cleaned_data['agree_with_decision']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm


def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))

