import itertools
import logging

from collections import Counter

from django import forms
from django.utils.translation import ugettext_lazy as _

from draw.models import Debate, DebateTeam
from participants.models import Speaker, Team
from tournaments.utils import get_side_name

from .result import ForfeitDebateResult, VotingDebateResult
from .utils import side_and_position_names

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
            self.password = tournament.pref('public_password')
        else:
            raise TypeError("'tournament' is a required keyword argument")
        kwargs.setdefault('label', "Tournament password")
        super(TournamentPasswordField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TournamentPasswordField, self).clean(value)
        if value != self.password:
            raise forms.ValidationError(_("That password isn't correct."))
        return value


class BaseScoreField(forms.FloatField):
    def __init__(self, *args, **kwargs):
        """Takes an additional optional keyword argument: preferences,
        the Preferences register for the Tournament."""

        tournament = kwargs.pop('tournament')
        if tournament:
            min_value  = tournament.pref(self.CONFIG_MIN_VALUE_FIELD)
            max_value  = tournament.pref(self.CONFIG_MAX_VALUE_FIELD)
            step_value = tournament.pref(self.CONFIG_STEP_VALUE_FIELD)
        else:
            min_value  = self.DEFAULT_MIN_VALUE
            max_value  = self.DEFAULT_MAX_VALUE
            step_value = self.DEFAULT_STEP_VALUE
        self.step_value = kwargs.get('step_value', step_value)

        kwargs.setdefault('min_value', self.coerce_for_ui(min_value))
        kwargs.setdefault('max_value', self.coerce_for_ui(max_value))

        super(BaseScoreField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(BaseScoreField, self).validate(value)
        self.check_value(value)

    def check_value(self, value):
        if value and self.step_value and value % self.step_value != 0:
            if self.step_value == 1:
                msg = 'Please enter a whole number.'
            else:
                msg = 'Please enter a multiple of %s.' % self.step_value
            raise forms.ValidationError(
                _(msg), code='decimal'
            )

    def widget_attrs(self, widget):
        attrs = super(BaseScoreField, self).widget_attrs(widget)
        if isinstance(widget, forms.NumberInput):
            attrs['step'] = self.coerce_for_ui(self.step_value) # override
        return attrs

    def coerce_for_ui(self, x):
        if x is None:
            return None
        if self.step_value % 1 == 0:
            return int(x)
        else:
            return float(x)


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
    DEFAULT_MIN_VALUE = 34.0
    DEFAULT_MAX_VALUE = 41.0
    DEFAULT_STEP_VALUE = 0.5


# ==============================================================================
# Result/ballot forms
# ==============================================================================

class BaseBallotSetForm(forms.Form):
    """Form for data entry for a single ballot set. Responsible for presenting
    the part that looks like a ballot, i.e. speaker names and scores for each
    adjudicator. Not responsible for controls that submit the form or anything
    like that.
    """

    confirmed = forms.BooleanField(required=False)
    discarded = forms.BooleanField(required=False)

    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

    SIDES = ['aff', 'neg']

    def __init__(self, ballotsub, *args, **kwargs):
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.adjudicators = list(self.debate.adjudicators.voting())
        self.motions = self.debate.round.motion_set
        self.tournament = self.debate.round.tournament
        self.using_motions = self.tournament.pref('enable_motions')
        self.using_vetoes = self.tournament.pref('motion_vetoes_enabled')
        self.using_forfeits = self.tournament.pref('enable_forfeits')
        self.using_replies = self.tournament.pref('reply_scores_enabled')
        self.choosing_sides = self.tournament.pref('draw_side_allocations') == 'manual-ballot'
        self.bypassing_checks = self.tournament.pref('disable_ballot_confirms')
        self.max_margin = self.tournament.pref('maximum_margin')
        self.score_step = self.tournament.pref('score_step')
        self.reply_score_step = self.tournament.pref('reply_score_step')

        self.has_tournament_password = kwargs.pop('password', False) and self.tournament.pref('public_use_password')

        super().__init__(*args, **kwargs)

        self.POSITIONS = self.tournament.POSITIONS
        self.LAST_SUBSTANTIVE_POSITION = self.tournament.LAST_SUBSTANTIVE_POSITION  # also used in template
        self.REPLY_POSITION = self.tournament.REPLY_POSITION  # also used in template

        self._create_fields()
        self._set_tab_indices()
        self.initial = self._initial_data()

    @property
    def SIDES_AND_POSITIONS(self):  # flake8: noqa
        return itertools.product(self.SIDES, self.POSITIONS)

    # --------------------------------------------------------------------------
    # Field names and field convenience functions
    # --------------------------------------------------------------------------

    def _side_name(self, side):
        return get_side_name(self.tournament, side, 'full')

    @staticmethod
    def _fieldname_motion_veto(side):
        return '%(side)s_motion_veto' % {'side': side}

    @staticmethod
    def _fieldname_speaker(side, pos):
        return '%(side)s_speaker_s%(pos)d' % {'side': side, 'pos': pos}

    @staticmethod
    def _fieldname_ghost(side, pos):
        return '%(side)s_ghost_s%(pos)d' % {'side': side, 'pos': pos}

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
         - aff/neg_ghost_s#,     whether score should be a duplicate
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
                choices=side_choices,
                coerce=lambda x: tuple(Team.objects.get(id=int(v)) for v in x.split(","))
            )
            for team in self.debate.teams:
                self.fields['team_%d' % team.id] = forms.ModelChoiceField(queryset=team.speakers, required=False)

        # 3. Motions fields
        if self.using_motions:
            self.fields['motion'] = MotionModelChoiceField(queryset=self.motions, required=True)

        if self.using_vetoes:
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

            # 4(b). Ghost fields
            self.fields[self._fieldname_ghost(side, pos)] = forms.BooleanField(required=False,
                label="Mark this as a duplicate speech")

            # 4(c). Speaker scores
            scorefield = ReplyScoreField if (pos == self.REPLY_POSITION) else SubstantiveScoreField
            for adj in self.adjudicators:
                self.fields[self._fieldname_score(adj, side, pos)] = scorefield(
                    widget=forms.NumberInput(attrs={'class': 'required number'}),
                    tournament=self.tournament)

        # 5. If forfeits are enabled, don't require some fields and add the forfeit field
        if self.using_forfeits:
            for side, pos in self.SIDES_AND_POSITIONS:
                self.fields[self._fieldname_speaker(side, pos)].required = False
                for adj in self.adjudicators:
                    self.fields[self._fieldname_score(adj, side, pos)].required = False
            if self.using_motions:
                self.fields['motion'].required = False

            choices = [(side, "Forfeit by the {}".format(self._side_name(side))) for side in self.SIDES]
            self.fields['forfeit'] = forms.ChoiceField(widget=forms.RadioSelect, choices=choices, required=False)

    def _initial_data(self):
        """Generates dictionary of initial form data."""

        result = VotingDebateResult(self.ballotsub)
        initial = {'debate_result_status': self.debate.result_status,
                   'confirmed': self.ballotsub.confirmed,
                   'discarded': self.ballotsub.discarded}

        # When bypassing confirmations we just pre-check
        if self.bypassing_checks:
            initial['confirmed'] = True
            # For new ballots default to confirmed status
            if self.debate.result_status == Debate.STATUS_NONE:
                initial['debate_result_status'] = Debate.STATUS_CONFIRMED

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
            if not self.ballotsub.motion and self.motions.count() == 1:
                initial['motion'] = self.motions.get()
            else:
                initial['motion'] = self.ballotsub.motion
            for side in self.SIDES:
                initial[self._fieldname_motion_veto(side)] = self.ballotsub.debateteammotionpreference_set.filter(
                        debate_team__side=side, preference=3).first()

        for side, pos in self.SIDES_AND_POSITIONS:
            speaker = result.get_speaker(side, pos)
            is_ghost = result.get_ghost(side, pos)
            if speaker:
                initial[self._fieldname_speaker(side, pos)] = speaker.pk
                initial[self._fieldname_ghost(side, pos)] = is_ghost

                for adj in self.adjudicators:
                    score = result.get_score(adj, side, pos)
                    coerce_for_ui = self.fields[self._fieldname_score(adj, side, pos)].coerce_for_ui
                    initial[self._fieldname_score(adj, side, pos)] = coerce_for_ui(score)

        if self.using_forfeits:
            forfeiter = self.ballotsub.teamscore_set.filter(forfeit=True, win=False).first()
            if forfeiter:
                initial['forfeit'] = forfeiter.debate_team.side

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

        order.append('ghost') # Dummy item; as input is created on the front end
        self.irontabindex = len(order) # Set the tab index it would have had

        for side, pos in self.SIDES_AND_POSITIONS:
            order.append(self._fieldname_speaker(side, pos))

        for adj, side, pos in itertools.product(self.adjudicators, self.SIDES, self.POSITIONS):
            order.append(self._fieldname_score(adj, side, pos))

        if 'password' in self.fields:
            order.append('password')
        if 'forfeit' in self.fields:
            order.append('forfeit')

        order.extend(['discarded', 'confirmed', 'debate_result_status'])

        if self.motions.count() <= 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.SIDES)

        # now, set
        for i, name in enumerate(order, start=1):
            try:
                self.fields[name].widget.attrs['tabindex'] = i
            except KeyError as e:
                logger.debug("Skipping tab index for field not found: %s", e)

        self.nexttabindex = i + 1  # for other UI elements in the tempate

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean(self):
        cleaned_data = super().clean()

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

        if not cleaned_data.get('forfeit'):
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

                    margin = abs(totals[0] - totals[1])
                    if self.max_margin and margin > self.max_margin:
                        self.add_error(None, forms.ValidationError(
                            _("The margin (%(margin).1f) in the ballot of adjudicator %(adj)s (%(adj_ins)s) exceeds the maximum allowable margin (%(max_margin).1f)"),
                            params={'adj': adj.name, 'adj_ins': adj.institution.code, 'margin': margin, 'max_margin': self.max_margin}, code='max_margin'
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
                for pos in range(1, self.LAST_SUBSTANTIVE_POSITION + 1):
                    speaker = self.cleaned_data.get(self._fieldname_speaker(side, pos))
                    if speaker is None:
                        logger.warning("Field '%s' not found", self._fieldname_speaker(side, pos))
                        continue

                    # The speaker must be on the relevant team.
                    if team is not None and speaker not in team.speakers:
                        self.add_error(self._fieldname_speaker(side, pos), forms.ValidationError(
                            _("The speaker %(speaker)s doesn't appear to be on team %(team)s."),
                            params={'speaker': speaker.name, 'team': team.short_name}, code='speaker_wrongteam')
                        )

                    # Don't increment the speaker count if the speech is marked as a ghost
                    if not self.cleaned_data.get(self._fieldname_ghost(side, pos)):
                        speaker_counts[speaker] += 1

                # The substantive speakers must be unique.
                for speaker, count in speaker_counts.items():
                    if count > 1:
                        self.add_error(None, forms.ValidationError(
                            _("The speaker %(speaker)s appears to have given multiple (%(count)d) substantive speeches for the %(side)s team."),
                            params={'speaker': speaker.name, 'side': self._side_name(side), 'count': count}, code='speaker_repeat'
                        ))

                if self.using_replies:
                    reply_speaker = cleaned_data.get(self._fieldname_speaker(side, self.REPLY_POSITION))
                    last_speaker = cleaned_data.get(self._fieldname_speaker(side, self.LAST_SUBSTANTIVE_POSITION))

                    # The third speaker can't give the reply.
                    if reply_speaker == last_speaker and reply_speaker is not None:
                        self.add_error(self._fieldname_speaker(side, self.REPLY_POSITION), forms.ValidationError(
                            _("The last substantive speaker and reply speaker for the %(side)s team can't be the same."),
                            params={'side': self._side_name(side)}, code='reply_speaker_consecutive'
                        ))

                    # The reply speaker must have given a substantive speech.
                    if speaker_counts[reply_speaker] == 0:
                        self.add_error(self._fieldname_speaker(side, self.REPLY_POSITION), forms.ValidationError(
                            _("The reply speaker for the %(side)s team did not give a substantive speech."),
                            params={'side': self._side_name(side)}, code='reply_speaker_not_repeat'
                        ))

        return cleaned_data

    def save(self):

        # 1. Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballotsub and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        # 2. Save ballot submission
        self.ballotsub.discarded = self.cleaned_data['discarded']
        self.ballotsub.confirmed = self.cleaned_data['confirmed']
        self.ballotsub.save()

        # 3. Check if there was a forfeit
        if self.using_forfeits and self.cleaned_data['forfeit']:
            result = ForfeitDebateResult(self.ballotsub, self.cleaned_data['forfeit'])
            self.ballotsub.forfeit = result.debateteams[self.cleaned_data['forfeit']]
        else:
            result = VotingDebateResult(self.ballotsub)

        # 4. Save the sides
        if self.choosing_sides:
            result.set_sides(*self.cleaned_data['choose_sides'])

        # 5. Save motions
        if self.using_motions:
            self.ballotsub.motion = self.cleaned_data['motion']

        if self.using_vetoes:
            for side in self.SIDES:
                motion_veto = self.cleaned_data[self._fieldname_motion_veto(side)]
                if motion_veto:
                    debate_team = self.debate.get_dt(side)
                    self.ballotsub.debateteammotionpreference_set.update_or_create(
                        debate_team=debate_team, preference=3,
                        defaults=dict(motion=motion_veto))

        # 6. Save speaker fields
        if not self.cleaned_data['forfeit']:
            for side, pos in self.SIDES_AND_POSITIONS:
                speaker = self.cleaned_data[self._fieldname_speaker(side, pos)]
                result.set_speaker(side, pos, speaker)
                is_ghost = self.cleaned_data[self._fieldname_ghost(side, pos)]
                result.set_ghost(side, pos, is_ghost)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self._fieldname_score(adj, side, pos)]
                    result.set_score(adj, side, pos, score)

        result.save()
        self.ballotsub.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

        return self.ballotsub

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def fake_speaker_selects(self):
        for team in self.debate.teams:
            yield self['team_%d' % team.id]

    def scoresheets(self):
        """Generates a sequence of nested dicts that allows for easy iteration
        through the form. Used in the enter_results_ballot_set.html template."""

        for adj in self.adjudicators:
            sheet_dict = {
                "adjudicator": adj,
                "teams": [],
            }
            for side, (side_name, pos_names) in zip(self.SIDES, side_and_position_names(self.tournament)):
                side_dict = {
                    "side_code": side,
                    "side_name": side_name,
                    "team": self.debate.get_team(side),
                    "speakers": [],
                }
                for pos, pos_name in zip(self.POSITIONS, pos_names):
                    side_dict["speakers"].append({
                        "pos": pos,
                        "name": pos_name,
                        "speaker": self[self._fieldname_speaker(side, pos)],
                        "ghost": self[self._fieldname_ghost(side, pos)],
                        "score": self[self._fieldname_score(adj, side, pos)],
                    })
                sheet_dict["teams"].append(side_dict)
            yield sheet_dict


class SingleBallotSetForm(BaseBallotSetForm):
    """Presents one ballot for the debate. Used for consensus adjudications."""
    pass


class PerAdjudicatorBallotSetForm(BaseBallotSetForm):
    """Presents one ballot per voting adjudicator. Used for voting
    adjudications."""
    pass
