from django import forms
import itertools
from collections import Counter
import logging

from draws.models import Debate, DebateTeam
from participants.models import Speaker, Team
from result import BallotSet


logger = logging.getLogger(__name__)

class FormConstructionError(Exception):
    pass

# ==============================================================================
# Result/ballot custom fields
# ==============================================================================

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

class MotionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%d. %s" % (obj.seq, obj.text)

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

    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

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
                choices=side_choices, coerce=lambda x: tuple(Team.objects.get(id=int(v)) for v in x.split(","))
            )
            for team in self.debate.teams:
                self.fields['team_%d' % team.id] = forms.ModelChoiceField(queryset=team.speakers, required=False)

        # 3. Motions fields
        if self.using_motions:
            self.fields['motion'] = MotionModelChoiceField(queryset=self.motions, required=True)
            for side in self.SIDES:
                self.fields[self._fieldname_motion_veto(side)] = MotionModelChoiceField(queryset=self.motions, required=False)

        # 4. Speaker fields
        for side, pos in self.SIDES_AND_POSITIONS:

            # 4(a). Speaker identity
            if self.choosing_sides:
                queryset = Speaker.objects.filter(team__in=self.debate.teams)
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
            except DebateTeam.DoesNotExist:
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

        if cleaned_data.get('debate_result_status') == Debate.STATUS_CONFIRMED and not cleaned_data.get('confirmed') and self.debate.confirmed_ballot is None:
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
                else:
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
