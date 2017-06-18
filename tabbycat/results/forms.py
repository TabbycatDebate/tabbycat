import logging
from itertools import product

from collections import Counter

from django import forms
from django.utils.translation import ugettext_lazy as _

from draw.models import Debate, DebateTeam
from participants.models import Speaker, Team
from tournaments.utils import get_side_name

from .result import ConsensusDebateResult, ForfeitDebateResult, VotingDebateResult
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
        """Takes an additional optional keyword argument: tournament,
        the Tournament used to configure the field."""

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
                msg = _("Please enter a whole number.")
            else:
                msg = _("Please enter a multiple of %s.") % self.step_value
            raise forms.ValidationError(msg, code='decimal')

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

    There are lots of fields that are conditionally displayed according to user
    preference. Most of these (for example, motions) are simply the presence or
    absence thereof, and it is easiest to govern these using if-else switches.
    For more involved customisations, like there is a ballot per adjudicator
    (voting) or a single ballot for the debate (consensus), we use subclasses.
    """

    confirmed = forms.BooleanField(required=False)
    discarded = forms.BooleanField(required=False)
    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

    result_class = None

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
        self.bypassing_checks = self.tournament.pref('disable_ballot_confirms')
        self.max_margin = self.tournament.pref('maximum_margin')
        self.choosing_sides = (self.tournament.pref('draw_side_allocations') == 'manual-ballot'
                               and self.tournament.pref('teams_in_debate') == 'two-team')

        self.has_tournament_password = kwargs.pop('password', False) and self.tournament.pref('public_use_password')

        super().__init__(*args, **kwargs)

        self.sides = self.tournament.sides
        self.positions = self.tournament.positions
        self.last_substantive_position = self.tournament.last_substantive_position  # also used in template
        self.reply_position = self.tournament.reply_position  # also used in template

        self.create_fields()
        self.set_tab_indices()
        self.initial = self.initial_data()

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

    # --------------------------------------------------------------------------
    # Form set-up
    # --------------------------------------------------------------------------

    def create_fields(self):
        """Dynamically generate fields for this ballot:
         - password
         - choose_sides,         if sides need to be chosen by the user
         - motion,               if there is more than one motion
         - <side>_motion_veto,   if motion vetoes are being noted, one for each team
         - <side>_speaker_s#,    one for each speaker
         - <side>_ghost_s#,      whether score should be a duplicate

        Most fields are required, unless forfeits are enabled.
        """

        dts = self.debate.debateteam_set.all()

        # 1. Tournament password field
        if self.has_tournament_password:
            self.fields['password'] = TournamentPasswordField(tournament=self.tournament)

        # 2. Choose sides field
        if self.choosing_sides:  # false in BP regardless of choosing sides setting
            teams = self.debate.teams
            assert len(teams) == 2
            side_choices = [
                (None, _("---------")),
                (str(teams[0].id) + "," + str(teams[1].id),
                    _("%(aff_team)s affirmed, %(neg_team)s negated") % {'aff_team': teams[0].short_name, 'neg_team': teams[1].short_name}),
                (str(teams[1].id) + "," + str(teams[0].id),
                    _("%(aff_team)s affirmed, %(neg_team)s negated") % {'aff_team': teams[1].short_name, 'neg_team': teams[0].short_name})
            ]
            self.fields['choose_sides'] = forms.TypedChoiceField(
                choices=side_choices,
                coerce=lambda x: tuple(Team.objects.get(id=int(v)) for v in x.split(","))
            )
            for team in self.debate.teams:
                self.fields['team_%d' % team.id] = forms.ModelChoiceField(queryset=team.speakers, required=False)

        # 3. Motions fields
        if self.using_motions:
            self.fields['motion'] = MotionModelChoiceField(queryset=self.motions,
                required=not self.using_forfeits)

        if self.using_vetoes:
            for side in self.sides:
                self.fields[self._fieldname_motion_veto(side)] = MotionModelChoiceField(
                    label=_("%(side_abbr)s's motion veto") % {'side_abbr': get_side_name(self.tournament, side, 'abbr')},
                    queryset=self.motions, required=False
                )

        # 4. Speaker fields
        for side, pos in product(self.sides, self.positions):

            # 4(a). Speaker identity
            if self.choosing_sides:
                queryset = Speaker.objects.filter(team__in=self.debate.teams)
            else:
                queryset = self.debate.get_team(side).speakers
            self.fields[self._fieldname_speaker(side, pos)] = forms.ModelChoiceField(
                queryset=queryset, required=not self.using_forfeits)

            # 4(b). Ghost fields
            self.fields[self._fieldname_ghost(side, pos)] = forms.BooleanField(required=False,
                label="Mark this as a duplicate speech")

        self.create_score_fields()

        # 5. Forfeit field
        if self.using_forfeits:
            choices = [(side, _("Forfeit by the %(side)s") % {'side': self._side_name(side)}) for side in self.sides]
            self.fields['forfeit'] = forms.ChoiceField(widget=forms.RadioSelect, choices=choices, required=False)

    def initial_data(self):
        """Generates dictionary of initial form data."""

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
            for side in self.sides:
                dtmp = self.ballotsub.debateteammotionpreference_set.filter(
                        debate_team__side=side, preference=3).first()
                if dtmp:
                    initial[self._fieldname_motion_veto(side)] = dtmp.motion

        if self.using_forfeits:
            forfeiter = self.ballotsub.teamscore_set.filter(forfeit=True, win=False).first()
            if forfeiter:
                initial['forfeit'] = forfeiter.debate_team.side

        result = self.result_class(self.ballotsub)
        initial.update(self.initial_from_result(result))

        return initial

    def initial_from_result(self, result):
        """Generates the initial from data that uses the DebateResult for the
        debate. Making this its own function allows subclasses to extend this so
        that it can use the same DebateResult as the super class."""
        initial = {}

        for side, pos in product(self.sides, self.positions):
            speaker = result.get_speaker(side, pos)
            is_ghost = result.get_ghost(side, pos)
            if speaker:
                initial[self._fieldname_speaker(side, pos)] = speaker.pk
                initial[self._fieldname_ghost(side, pos)] = is_ghost

        return initial

    def set_tab_indices(self):
        """Sets all the tab indices in the form."""
        # make a list for field names, then set them all at the end
        order = list()

        if 'choose_sides' in self.fields:
            order.append('choose_sides')

        if self.motions.count() > 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.sides)

        order.append('ghost') # Dummy item; as input is created on the front end
        self.irontabindex = len(order) # Set the tab index it would have had

        for side, pos in product(self.sides, self.positions):
            order.append(self._fieldname_speaker(side, pos))

        order.extend(self.list_score_fields())

        if 'password' in self.fields:
            order.append('password')
        if 'forfeit' in self.fields:
            order.append('forfeit')

        order.extend(['discarded', 'confirmed', 'debate_result_status'])

        if self.motions.count() <= 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.sides)

        # now, set
        for i, name in enumerate(order, start=1):
            try:
                self.fields[name].widget.attrs['tabindex'] = i
            except KeyError as e:
                logger.debug("Skipping tab index for field not found: %s", e)

        self.nexttabindex = i + 1  # for other UI elements in the tempate

    def list_score_fields(self):
        """Should be overridden by subclasses; the default implementation
        returns an empty list."""
        return []

    # --------------------------------------------------------------------------
    # Validation methods
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
            self.clean_speakers(cleaned_data)
            self.clean_scoresheet(cleaned_data)

        return cleaned_data

    def clean_speakers(self, cleaned_data):
        """Checks that the speaker selections are valid."""

        # Pull team info again, in case it's changed since the form was loaded.
        if self.choosing_sides:
            teams = cleaned_data.get('choose_sides', [None] * len(self.sides))
        else:
            teams = [self.debate.get_team(side) for side in self.sides]
        if None in teams:
            logger.warning("Team identities not found")

        for side, team in zip(self.sides, teams):

            speaker_counts = Counter()
            for pos in range(1, self.last_substantive_position + 1):
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
                reply_speaker = cleaned_data.get(self._fieldname_speaker(side, self.reply_position))
                last_speaker = cleaned_data.get(self._fieldname_speaker(side, self.last_substantive_position))

                # The last speaker can't give the reply.
                if reply_speaker == last_speaker and reply_speaker is not None:
                    self.add_error(self._fieldname_speaker(side, self.reply_position), forms.ValidationError(
                        _("The last substantive speaker and reply speaker for the %(side)s team can't be the same."),
                        params={'side': self._side_name(side)}, code='reply_speaker_consecutive'
                    ))

                # The reply speaker must have given a substantive speech.
                if speaker_counts[reply_speaker] == 0:
                    self.add_error(self._fieldname_speaker(side, self.reply_position), forms.ValidationError(
                        _("The reply speaker for the %(side)s team did not give a substantive speech."),
                        params={'side': self._side_name(side)}, code='reply_speaker_not_repeat'
                    ))

    def clean_scoresheet(self, cleaned_data):
        """Cleans the speaker score fields.
        Must be implemented by subclasses."""
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # Saving
    # --------------------------------------------------------------------------

    def save(self):

        # 1. Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballotsub and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        # 2. Save ballot submission so that we can create related objects
        if self.ballotsub.pk is None:
            self.ballotsub.save()

        # 3. Check if there was a forfeit
        if self.using_forfeits and self.cleaned_data.get('forfeit'):
            result = ForfeitDebateResult(self.ballotsub, self.cleaned_data['forfeit'])
            self.ballotsub.forfeit = result.debateteams[self.cleaned_data['forfeit']]
        else:
            result = self.result_class(self.ballotsub)

        # 4. Save the sides
        if self.choosing_sides:
            result.set_sides(*self.cleaned_data['choose_sides'])

        # 5. Save motions
        if self.using_motions:
            self.ballotsub.motion = self.cleaned_data['motion']

        if self.using_vetoes:
            for side in self.sides:
                motion_veto = self.cleaned_data[self._fieldname_motion_veto(side)]
                debate_team = self.debate.get_dt(side)
                if motion_veto:
                    self.ballotsub.debateteammotionpreference_set.update_or_create(
                        debate_team=debate_team, preference=3,
                        defaults=dict(motion=motion_veto))
                else:
                    self.ballotsub.debateteammotionpreference_set.filter(
                        debate_team=debate_team, preference=3).delete()

        # 6. Save speaker fields
        if not self.using_forfeits or not self.cleaned_data.get('forfeit'):
            for side, pos in product(self.sides, self.positions):
                speaker = self.cleaned_data[self._fieldname_speaker(side, pos)]
                result.set_speaker(side, pos, speaker)
                is_ghost = self.cleaned_data[self._fieldname_ghost(side, pos)]
                result.set_ghost(side, pos, is_ghost)

            self.populate_result_with_scores(result)

        result.save()

        self.ballotsub.discarded = self.cleaned_data['discarded']
        self.ballotsub.confirmed = self.cleaned_data['confirmed']
        self.ballotsub.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

        return self.ballotsub

    def populate_result_with_scores(self, result):
        """Should populate `result` with speaker scores in-place, using the data
        in `self.cleaned_data`. Must be implemented by subclasses."""
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def fake_speaker_selects(self):
        for team in self.debate.teams:
            yield self['team_%d' % team.id]

    def motion_veto_fields(self):
        """Generator to allow easy iteration through the motion veto fields."""
        for side in self.sides:
            yield self[self._fieldname_motion_veto(side)]

    def scoresheet(self, fieldname_score_func):
        """Returns a list of dictionaries for a single scoresheet, to allow for
        easy iteration of the form. The function `fieldname_score_func` should
        take two arguments `(side, pos)`. This function is called by the
        `.scoresheets()` methods of both subclasses."""
        teams = []
        for side, (side_name, pos_names) in zip(self.sides, side_and_position_names(self.tournament)):
            side_dict = {
                "side_code": side,
                "side_name": side_name,
                "team": self.debate.get_team(side),
                "speakers": [],
            }
            for pos, pos_name in zip(self.positions, pos_names):
                side_dict["speakers"].append({
                    "pos": pos,
                    "name": pos_name,
                    "speaker": self[self._fieldname_speaker(side, pos)],
                    "ghost": self[self._fieldname_ghost(side, pos)],
                    "score": self[fieldname_score_func(side, pos)],
                })
            teams.append(side_dict)
        return teams


class SingleBallotSetForm(BaseBallotSetForm):
    """Presents one ballot for the debate. Used for consensus adjudications."""

    result_class = ConsensusDebateResult

    @staticmethod
    def _fieldname_score(side, pos):
        return '%(side)s_score_s%(pos)d' % {'side': side, 'pos': pos}

    def create_score_fields(self):
        """Adds the speaker score fields:
         - <side>_score_s#,  one for each score
        """
        for side, pos in product(self.sides, self.positions):
            scorefield = ReplyScoreField if (pos == self.reply_position) else SubstantiveScoreField
            self.fields[self._fieldname_score(side, pos)] = scorefield(
                widget=forms.NumberInput(attrs={'class': 'required number'}),
                tournament=self.tournament,
                required=not self.using_forfeits,
            )

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)

        for side, pos in product(self.sides, self.positions):
            score = result.get_score(side, pos)
            coerce_for_ui = self.fields[self._fieldname_score(side, pos)].coerce_for_ui
            initial[self._fieldname_score(side, pos)] = coerce_for_ui(score)

        return initial

    def list_score_fields(self):
        """Lists all the score fields. Called by super().set_tab_indices()."""
        order = []
        for side, pos in product(self.sides, self.positions):
            order.append(self._fieldname_score(side, pos))
        return order

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean_scoresheet(self, cleaned_data):
        try:
            totals = [sum(cleaned_data[self._fieldname_score(side, pos)]
                       for pos in self.positions) for side in self.sides]

        except KeyError as e:
            logger.warning("Field %s not found", str(e))

        else:
            # Check that no teams had the same total.
            if len(totals) == 2 and totals[0] == totals[1]:
                self.add_error(None, forms.ValidationError(
                    _("The total scores for the teams are the same (i.e. a draw)."),
                    code='draw'
                ))

            elif len(totals) > 2:
                for total in set(totals):
                    sides = [s for s, t in zip(self.sides, totals) if t == total]
                    if len(sides) > 1:
                        self.add_error(None, forms.ValidationError(
                            _("The total scores for the following teams are the same: %(teams)s"),
                            params={'teams': ", ".join(self._side_name(side) for side in sides)},
                            code='tied_score'
                        ))

            # Check that the margin did not exceed the maximum permissible.
            if len(totals) == 2 and self.max_margin:
                margin = abs(totals[0] - totals[1])
                if margin > self.max_margin:
                    self.add_error(None, forms.ValidationError(
                        _("The margin (%(margin).1f) exceeds the maximum allowable margin (%(max_margin).1f)."),
                        params={'margin': margin, 'max_margin': self.max_margin}, code='max_margin'
                    ))

    def populate_result_with_scores(self, result):
        for side, pos in product(self.sides, self.positions):
            score = self.cleaned_data[self._fieldname_score(side, pos)]
            result.set_score(side, pos, score)

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def scoresheets(self):
        """Generates a sequence of nested dicts that allows for easy iteration
        through the form. Used in the enter_results_ballot_set.html template."""
        return [{"teams": self.scoresheet(self._fieldname_score)}]


class PerAdjudicatorBallotSetForm(BaseBallotSetForm):
    """Presents one ballot per voting adjudicator. Used for voting
    adjudications."""

    result_class = VotingDebateResult

    @staticmethod
    def _fieldname_score(adj, side, pos):
        return '%(side)s_score_a%(adj)d_s%(pos)d' % {'adj': adj.id, 'side': side, 'pos': pos}

    def create_score_fields(self):
        """Adds the speaker score fields:
         - <side>_score_a#_s#,  one for each score
        """
        for side, pos in product(self.sides, self.positions):
            scorefield = ReplyScoreField if (pos == self.reply_position) else SubstantiveScoreField
            for adj in self.adjudicators:
                self.fields[self._fieldname_score(adj, side, pos)] = scorefield(
                    widget=forms.NumberInput(attrs={'class': 'required number'}),
                    tournament=self.tournament,
                    required=not self.using_forfeits,
                )

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)

        for adj, side, pos in product(self.adjudicators, self.sides, self.positions):
            score = result.get_score(adj, side, pos)
            coerce_for_ui = self.fields[self._fieldname_score(adj, side, pos)].coerce_for_ui
            initial[self._fieldname_score(adj, side, pos)] = coerce_for_ui(score)

        return initial

    def list_score_fields(self):
        """Lists all the score fields. Called by super().set_tab_indices()."""
        order = []
        for adj, side, pos in product(self.adjudicators, self.sides, self.positions):
            order.append(self._fieldname_score(adj, side, pos))
        return order

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean_scoresheet(self, cleaned_data):
        for adj in self.adjudicators:
            try:
                totals = [sum(cleaned_data[self._fieldname_score(adj, side, pos)]
                           for pos in self.positions) for side in self.sides]

            except KeyError as e:
                logger.warning("Field %s not found", str(e))

            else:
                # Check that it was not a draw.
                if totals[0] == totals[1]:
                    self.add_error(None, forms.ValidationError(
                        _("The total scores for the teams are the same (i.e. a draw) for adjudicator %(adj)s (%(adj_ins)s)."),
                        params={'adj': adj.name, 'adj_ins': adj.institution.code}, code='draw'
                    ))

                # Check that the margin did not exceed the maximum permissible.
                margin = abs(totals[0] - totals[1])
                if self.max_margin and margin > self.max_margin:
                    self.add_error(None, forms.ValidationError(
                        _("The margin (%(margin).1f) in the ballot of adjudicator %(adj)s (%(adj_ins)s) exceeds the maximum allowable margin (%(max_margin).1f)."),
                        params={'adj': adj.name, 'adj_ins': adj.institution.code, 'margin': margin, 'max_margin': self.max_margin}, code='max_margin'
                    ))

    def populate_result_with_scores(self, result):
        for adj, side, pos in product(self.adjudicators, self.sides, self.positions):
                score = self.cleaned_data[self._fieldname_score(adj, side, pos)]
                result.set_score(adj, side, pos, score)

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def scoresheets(self):
        """Generates a sequence of nested dicts that allows for easy iteration
        through the form. Used in the enter_results_ballot_set.html template."""

        for adj in self.adjudicators:
            sheet_dict = {
                "adjudicator": adj,
                "teams": self.scoresheet(
                    lambda side, pos: self._fieldname_score(adj, side, pos)
                ),
            }
            yield sheet_dict
