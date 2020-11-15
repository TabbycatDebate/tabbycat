import logging
from itertools import product

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from draw.models import Debate, DebateTeam
from participants.models import Speaker, Team
from tournaments.utils import get_side_name

from .consumers import BallotResultConsumer, BallotStatusConsumer
from .result import (ConsensusDebateResult, ConsensusDebateResultWithScores,
                     DebateResultByAdjudicator, DebateResultByAdjudicatorWithScores)
from .utils import get_status_meta, side_and_position_names

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
        kwargs.setdefault('label', _("Tournament password"))
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
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

        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        self.check_value(value)

    def check_value(self, value):
        if value and self.step_value and value % self.step_value != 0:
            if self.step_value == 1:
                msg = _("Please enter a whole number.")
            else:
                msg = _("Please enter a multiple of %s.") % self.step_value
            raise forms.ValidationError(msg, code='decimal')

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
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

class BaseResultForm(forms.Form):
    """Base class for forms that report results. Contains fields and methods
    common to absolutely everything (which isn't very much)."""

    confirmed = forms.BooleanField(required=False)
    discarded = forms.BooleanField(required=False)

    def __init__(self, ballotsub, password=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.tournament = self.debate.round.tournament

        self.has_tournament_password = password and self.tournament.pref('public_use_password')

        status_choices = Debate.STATUS_CHOICES if self.tournament.pref('enable_postponements') else Debate.STATUS_CHOICES_RESTRICTED
        self.fields['debate_result_status'] = forms.ChoiceField(choices=status_choices)

        self.initial.update({
            'debate_result_status': self.debate.result_status,
            'confirmed': self.ballotsub.confirmed,
            'discarded': self.ballotsub.discarded,
        })

        if self.has_tournament_password:
            self.fields['password'] = TournamentPasswordField(tournament=self.tournament)

    def _side_name(self, side):
        return get_side_name(self.tournament, side, 'full')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('discarded') and cleaned_data.get('confirmed'):
            for field in ('discarded', 'confirmed'):
                self.add_error(field, forms.ValidationError(
                    _("The ballot set can't be both discarded and confirmed."),
                    code='discard_confirm',
                ))

        data_confirmed = cleaned_data.get('debate_result_status') == Debate.STATUS_CONFIRMED and not cleaned_data.get('confirmed')
        if data_confirmed and self.debate.confirmed_ballot is None:
            self.add_error('debate_result_status', forms.ValidationError(
                _("The debate status can't be confirmed unless one of the ballot sets is confirmed."),
                code='status_confirm',
            ))

        return cleaned_data

    def save(self):

        # 1. Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballotsub and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        # 2. Save ballot submission so that we can create related objects
        if self.ballotsub.id is None:
            self.ballotsub.save()

        # 3. Save the specifics of the ballot
        self.save_ballot()

        # 4. Save ballot and result status
        self.ballotsub.discarded = self.cleaned_data['discarded']
        self.ballotsub.confirmed = self.cleaned_data['confirmed']
        self.ballotsub.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

        t = self.debate.round.tournament
        # Need to provide a timestamp immediately for BallotStatusConsumer
        # as it will broadcast before the view finishes assigning one
        if self.ballotsub.confirmed:
            self.ballotsub.confirm_timestamp = timezone.now()

            # 5. Notify the Latest Results consumer (for results/overview)
            if self.debate.result_status == Debate.STATUS_CONFIRMED:
                group_name = BallotResultConsumer.group_prefix + "_" + t.slug
                async_to_sync(get_channel_layer().group_send)(group_name, {
                    "type": "send_json",
                    "data": self.ballotsub.serialize_like_actionlog,
                })

        # 6. Notify the Results Page/Ballots Status Graph
        group_name = BallotStatusConsumer.group_prefix + "_" + t.slug
        meta = get_status_meta(self.debate)
        async_to_sync(get_channel_layer().group_send)(group_name, {
            "type": "send_json",
            "data": {
                'status': self.debate.result_status,
                'icon': meta[0],
                'class': meta[1],
                'sort': meta[2],
                'ballot': self.ballotsub.serialize(t),
                'round': self.debate.round_id,
            },
        })

        return self.ballotsub

    def save_ballot(self):
        raise NotImplementedError


class BaseBallotSetForm(BaseResultForm):
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

    result_class = None

    def __init__(self, ballotsub, *args, **kwargs):
        super().__init__(ballotsub, *args, **kwargs)

        self.adjudicators = list(self.debate.adjudicators.voting())
        self.motions = self.debate.round.motion_set

        self.using_motions = self.tournament.pref('enable_motions')
        self.using_vetoes = self.tournament.pref('motion_vetoes_enabled')
        self.using_replies = self.tournament.pref('reply_scores_enabled')
        self.using_declared_winner = self.tournament.pref('winners_in_ballots') != 'none'
        self.declared_winner = self.tournament.pref('winners_in_ballots')
        self.bypassing_checks = self.tournament.pref('disable_ballot_confirms')
        self.max_margin = self.tournament.pref('maximum_margin')
        self.choosing_sides = (self.tournament.pref('draw_side_allocations') == 'manual-ballot' and
                               self.tournament.pref('teams_in_debate') == 'two')

        self.sides = self.tournament.sides
        self.positions = self.tournament.positions
        self.last_substantive_position = self.tournament.last_substantive_position  # also used in template
        self.reply_position = self.tournament.reply_position  # also used in template

        self.create_fields()
        self.set_tab_indices()
        self.initial.update(self.initial_data())

    # --------------------------------------------------------------------------
    # Field names and field convenience functions
    # --------------------------------------------------------------------------

    @staticmethod
    def _fieldname_motion_veto(side):
        return '%(side)s_motion_veto' % {'side': side}

    # --------------------------------------------------------------------------
    # Form set-up
    # --------------------------------------------------------------------------

    def create_fields(self):
        """Dynamically generate fields for this ballot:
         - choose_sides,         if sides need to be chosen by the user
         - motion,               if there is more than one motion
         - <side>_motion_veto,   if motion vetoes are being noted, one for each team
         - <side>_speaker_s#,    one for each speaker
         - <side>_ghost_s#,      whether score should be a duplicate
        """

        # 1. Choose sides field
        if self.choosing_sides:  # false in BP regardless of choosing sides setting
            teams = self.debate.teams
            assert len(teams) == 2
            side_choices = [
                (None, _("---------")),
                (str(teams[0].id) + "," + str(teams[1].id),
                    _("%(aff_team)s affirmed, %(neg_team)s negated") % {'aff_team': teams[0].short_name, 'neg_team': teams[1].short_name}),
                (str(teams[1].id) + "," + str(teams[0].id),
                    _("%(aff_team)s affirmed, %(neg_team)s negated") % {'aff_team': teams[1].short_name, 'neg_team': teams[0].short_name}),
            ]
            self.fields['choose_sides'] = forms.TypedChoiceField(
                choices=side_choices,
                coerce=lambda x: tuple(Team.objects.get(id=int(v)) for v in x.split(",")),
            )
            for team in self.debate.teams:
                self.fields['team_%d' % team.id] = forms.ModelChoiceField(queryset=team.speakers, required=False)

        # 2. Motions fields
        if self.using_motions:
            self.fields['motion'] = MotionModelChoiceField(queryset=self.motions,
                required=True)

        if self.using_vetoes:
            for side in self.sides:
                self.fields[self._fieldname_motion_veto(side)] = MotionModelChoiceField(
                    label=_("%(side)s's motion veto") % {'side': get_side_name(self.tournament, side, 'abbr')},
                    queryset=self.motions, required=False, help_text=get_side_name(self.tournament, side, 'full'),
                )

        # 3. Speaker fields
        self.create_participant_fields()

    def create_declared_winner_dropdown(self):
        """This method creates a drop-down with a list of the teams in the debate"""
        teams = [(s, _("%(team)s (%(side)s)") % {
            'team': self.debate.get_team(s).short_name, 'side': get_side_name(self.tournament, s, 'full')}) for s in self.sides]
        return forms.TypedChoiceField(
            label=_("Winner"), required=True, empty_value=None,
            choices=[(None, _("---------"))] + teams,
        )

    def initial_data(self):
        """Generates dictionary of initial form data."""

        initial = {}

        # When bypassing confirmations we just pre-check
        if self.bypassing_checks:
            initial['confirmed'] = True
            # For new ballots default to confirmed status
            if self.debate.result_status == Debate.STATUS_NONE:
                initial['debate_result_status'] = Debate.STATUS_CONFIRMED

        # If sides are already confirmed, initialise the choose sides field
        if self.choosing_sides and self.ballotsub.debate.sides_confirmed:
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

        if self.using_vetoes:
            for side in self.sides:
                dtmp = self.ballotsub.debateteammotionpreference_set.filter(
                        debate_team__side=side, preference=3).first()
                if dtmp:
                    initial[self._fieldname_motion_veto(side)] = dtmp.motion

        result = self.result_class(self.ballotsub)
        initial.update(self.initial_from_result(result))

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

        order.extend(self.list_participant_fields())
        order.extend(self.list_score_fields())

        if 'password' in self.fields:
            order.append('password')

        order.extend(['confirmed', 'discarded', 'debate_result_status'])

        if self.motions.count() <= 1:
            order.append('motion')
            order.extend(self._fieldname_motion_veto(side) for side in self.sides)

        # now, set
        for i, name in enumerate(order, start=3): # Start at 3 to account for front-end only fields
            try:
                self.fields[name].widget.attrs['tabindex'] = i
            except KeyError as e:
                logger.debug("Skipping tab index for field not found: %s", e)

        self.nexttabindex = i + 1  # for other UI elements in the tempate

    # --------------------------------------------------------------------------
    # Saving
    # --------------------------------------------------------------------------

    def save_ballot(self):

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

        # 6. Save participant fields
        self.save_participant_fields(result)

        result.save()

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def motion_veto_fields(self):
        """Generator to allow easy iteration through the motion veto fields."""
        for side in self.sides:
            yield self[self._fieldname_motion_veto(side)]


class ScoresMixin:

    has_scores = True

    # --------------------------------------------------------------------------
    # Field names and field convenience functions
    # --------------------------------------------------------------------------

    @staticmethod
    def _fieldname_speaker(side, pos):
        return '%(side)s_speaker_s%(pos)d' % {'side': side, 'pos': pos}

    @staticmethod
    def _fieldname_ghost(side, pos):
        return '%(side)s_ghost_s%(pos)d' % {'side': side, 'pos': pos}

    # --------------------------------------------------------------------------
    # Form set-up
    # --------------------------------------------------------------------------

    def create_participant_fields(self):
        for side, pos in product(self.sides, self.positions):

            # 3(a). Speaker identity
            if self.choosing_sides:
                queryset = Speaker.objects.filter(team__in=self.debate.teams)
            else:
                queryset = self.debate.get_team(side).speakers
            self.fields[self._fieldname_speaker(side, pos)] = forms.ModelChoiceField(
                queryset=queryset, required=True)

            # 3(b). Ghost fields
            self.fields[self._fieldname_ghost(side, pos)] = forms.BooleanField(required=False,
                label=_("Mark as a duplicate speech"), label_suffix="")

        self.create_score_fields()

    def list_participant_fields(self):
        order = []
        for side, pos in product(self.sides, self.positions):
            order.append(self._fieldname_speaker(side, pos))
        return order

    def list_score_fields(self):
        """Should be overridden by subclasses; the default implementation
        returns an empty list."""
        return []

    def initial_from_result(self, result):
        """Generates the initial from data that uses the DebateResult for the
        debate. Making this its own function allows subclasses to extend this so
        that it can use the same DebateResult as the super class."""
        initial = {}
        for side, pos in product(self.sides, self.positions):
            initial[self._fieldname_speaker(side, pos)] = result.get_speaker(side, pos)
            initial[self._fieldname_ghost(side, pos)] = result.get_ghost(side, pos)
        return initial

    # --------------------------------------------------------------------------
    # Validation methods
    # --------------------------------------------------------------------------

    def clean(self):
        cleaned_data = super().clean()

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

            speaker_positions = dict()
            for pos in range(1, self.last_substantive_position + 1):
                speaker = cleaned_data.get(self._fieldname_speaker(side, pos))
                if speaker is None:
                    logger.warning("Field '%s' not found", self._fieldname_speaker(side, pos))
                    continue

                # The speaker must be on the relevant team.
                if team is not None and speaker not in team.speakers:
                    self.add_error(self._fieldname_speaker(side, pos), forms.ValidationError(
                        _("The speaker %(speaker)s doesn't appear to be on team %(team)s."),
                        params={'speaker': speaker.name, 'team': team.short_name},
                        code='speaker_wrongteam'),
                    )

                # Don't count this speaker if the speech is marked as a ghost
                if not cleaned_data.get(self._fieldname_ghost(side, pos)):
                    speaker_positions.setdefault(speaker, []).append(pos)

            # The substantive speakers must be unique.
            for speaker, positions in speaker_positions.items():
                if len(positions) > 1:
                    # Translators: count is always at least 2
                    message = ngettext(
                        "%(speaker)s appears to have given %(count)d substantive speech.",  # never used, needed for i18n
                        "%(speaker)s appears to have given %(count)d substantive speeches.",
                        len(positions),
                    )
                    params = {'speaker': speaker.name, 'count': len(positions)}
                    for pos in positions:
                        self.add_error(self._fieldname_speaker(side, pos), forms.ValidationError(
                            message, params=params, code='speaker_repeat'))

            # Check reply speaker only if not marked as a ghost
            if self.using_replies and not cleaned_data.get(self._fieldname_ghost(side, self.reply_position)):
                reply_speaker = cleaned_data.get(self._fieldname_speaker(side, self.reply_position))
                last_speaker = cleaned_data.get(self._fieldname_speaker(side, self.last_substantive_position))

                # The last speaker can't give the reply.
                if reply_speaker == last_speaker and reply_speaker is not None:
                    self.add_error(self._fieldname_speaker(side, self.reply_position), forms.ValidationError(
                        _("The last substantive speaker and reply speaker can't be the same."),
                        code='reply_speaker_consecutive',
                    ))

                # The reply speaker must have given a substantive speech.
                if self.tournament.pref('require_substantive_for_reply') and len(speaker_positions.get(reply_speaker, [])) == 0:
                    self.add_error(self._fieldname_speaker(side, self.reply_position), forms.ValidationError(
                        _("The reply speaker for this team did not give a substantive speech."),
                        code='reply_speaker_not_repeat',
                    ))

    def clean_scoresheet(self, cleaned_data):
        """Cleans the speaker score fields.
        Must be implemented by subclasses."""
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # Saving
    # --------------------------------------------------------------------------

    def save_participant_fields(self, result):
        for side, pos in product(self.sides, self.positions):
            speaker = self.cleaned_data[self._fieldname_speaker(side, pos)]
            result.set_speaker(side, pos, speaker)
            is_ghost = self.cleaned_data[self._fieldname_ghost(side, pos)]
            result.set_ghost(side, pos, is_ghost)

        self.populate_result_with_scores(result)

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


class SingleBallotSetForm(ScoresMixin, BaseBallotSetForm):
    """Presents one ballot for the debate. Used for consensus adjudications."""

    result_class = ConsensusDebateResultWithScores

    @staticmethod
    def _fieldname_score(side, pos):
        return '%(side)s_score_s%(pos)d' % {'side': side, 'pos': pos}

    @staticmethod
    def _fieldname_declared_winner():
        return 'declared_winner'

    def create_score_fields(self):
        """Adds the speaker score fields:
         - <side>_score_s#,  one for each score
        """
        for side, pos in product(self.sides, self.positions):
            scorefield = ReplyScoreField if (pos == self.reply_position) else SubstantiveScoreField
            self.fields[self._fieldname_score(side, pos)] = scorefield(
                widget=forms.NumberInput(attrs={'class': 'required number'}),
                tournament=self.tournament,
                required=True,
            )

        if self.using_declared_winner:
            self.fields[self._fieldname_declared_winner()] = self.create_declared_winner_dropdown()

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)

        for side, pos in product(self.sides, self.positions):
            score = result.get_score(side, pos)
            coerce_for_ui = self.fields[self._fieldname_score(side, pos)].coerce_for_ui
            initial[self._fieldname_score(side, pos)] = coerce_for_ui(score)

        if self.using_declared_winner:
            initial[self._fieldname_declared_winner()] = result.winning_side()

        return initial

    def list_score_fields(self):
        """Lists all the score fields. Called by super().set_tab_indices()."""
        order = []
        for side, pos in product(self.sides, self.positions):
            order.append(self._fieldname_score(side, pos))

        if self.using_declared_winner:
            order.append(self._fieldname_declared_winner())
        return order

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean_scoresheet(self, cleaned_data):
        try:
            side_totals = {side: sum(cleaned_data[self._fieldname_score(side, pos)]
                           for pos in self.positions) for side in self.sides}
            totals = list(side_totals.values())

        except KeyError as e:
            logger.warning("Field %s not found", str(e))

        else:
            if len(totals) == 2:
                max_teams = [side for side, total in side_totals.items() if total == max(totals)]
                high_point_declared = cleaned_data.get(self._fieldname_declared_winner()) in max_teams

                # Check that no teams had the same total
                if totals[0] == totals[1] and self.declared_winner in ['none', 'high-points']:
                    self.add_error(None, forms.ValidationError(
                        _("The total scores for the teams are the same (i.e. a draw)."),
                        code='draw',
                    ))
                elif self.declared_winner in ['high-points', 'tied-points'] and not high_point_declared:
                    self.add_error(None, forms.ValidationError(
                        _("The declared winner does not correspond to the team with the highest score."),
                        code='wrong_winner',
                    ))

            elif len(totals) > 2:
                for total in set(totals):
                    sides = [s for s, t in zip(self.sides, totals) if t == total]
                    if len(sides) > 1:
                        self.add_error(None, forms.ValidationError(
                            _("The total scores for the following teams are the same: %(teams)s"),
                            params={'teams': ", ".join(self._side_name(side) for side in sides)},
                            code='tied_score',
                        ))

            # Check that the margin did not exceed the maximum permissible.
            if len(totals) == 2 and self.max_margin:
                margin = abs(totals[0] - totals[1])
                if margin > self.max_margin:
                    self.add_error(None, forms.ValidationError(
                        _("The margin (%(margin).1f) exceeds the maximum allowable margin (%(max_margin).1f)."),
                        params={'margin': margin, 'max_margin': self.max_margin}, code='max_margin',
                    ))

    def populate_result_with_scores(self, result):
        for side, pos in product(self.sides, self.positions):
            score = self.cleaned_data[self._fieldname_score(side, pos)]
            result.set_score(side, pos, score)

        if self.declared_winner not in ['none', 'high-points']:
            result.set_winners(set([self.cleaned_data[self._fieldname_declared_winner()]]))

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def scoresheets(self):
        """Generates a sequence of nested dicts that allows for easy iteration
        through the form. Used in the ballot_set.html.html template."""
        sheets = [{"teams": self.scoresheet(self._fieldname_score)}]

        if self.using_declared_winner:
            sheets[0]['declared_winner'] = self[self._fieldname_declared_winner()]
        return sheets


class PerAdjudicatorBallotSetForm(ScoresMixin, BaseBallotSetForm):
    """Presents one ballot per voting adjudicator. Used for voting
    adjudications."""

    result_class = DebateResultByAdjudicatorWithScores

    @staticmethod
    def _fieldname_score(adj, side, pos):
        return '%(side)s_score_a%(adj)d_s%(pos)d' % {'adj': adj.id, 'side': side, 'pos': pos}

    @staticmethod
    def _fieldname_declared_winner(adj):
        return 'declared_winner_a%(adj)d' % {'adj': adj.id}

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
                    required=True,
                )
        if self.using_declared_winner:
            for adj in self.adjudicators:
                self.fields[self._fieldname_declared_winner(adj)] = self.create_declared_winner_dropdown()

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)

        for adj in self.adjudicators:
            for side, pos in product(self.sides, self.positions):
                score = result.get_score(adj, side, pos)
                coerce_for_ui = self.fields[self._fieldname_score(adj, side, pos)].coerce_for_ui
                initial[self._fieldname_score(adj, side, pos)] = coerce_for_ui(score)

            if self.using_declared_winner:
                initial[self._fieldname_declared_winner(adj)] = result.get_winner(adj)

        return initial

    def list_score_fields(self):
        """Lists all the score fields. Called by super().set_tab_indices()."""
        order = []
        for adj in self.adjudicators:
            for side, pos in product(self.sides, self.positions):
                order.append(self._fieldname_score(adj, side, pos))

            if self.using_declared_winner:
                order.append(self._fieldname_declared_winner(adj))
        return order

    # --------------------------------------------------------------------------
    # Validation and save methods
    # --------------------------------------------------------------------------

    def clean_scoresheet(self, cleaned_data):
        for adj in self.adjudicators:
            try:
                side_totals = {side: sum(cleaned_data[self._fieldname_score(adj, side, pos)]
                           for pos in self.positions) for side in self.sides}
                totals = list(side_totals.values())

            except KeyError as e:
                logger.warning("Field %s not found", str(e))

            else:
                if len(totals) == 2:
                    max_teams = [side for side, total in side_totals.items() if total == max(totals)]
                    high_point_declared = cleaned_data.get(self._fieldname_declared_winner(adj)) in max_teams

                    # Check that it was not a draw.
                    if totals[0] == totals[1] and self.declared_winner in ['none', 'high-points']:
                        self.add_error(None, forms.ValidationError(
                            _("The total scores for the teams are the same (i.e. a draw) for adjudicator %(adjudicator)s."),
                            params={'adjudicator': adj.name}, code='draw',
                        ))
                    elif self.declared_winner in ['high-points', 'tied-points'] and not high_point_declared:
                        self.add_error(None, forms.ValidationError(
                            _("The declared winner does not correspond to the team with the highest score for adjudicator %(adjudicator)s."),
                            params={'adjudicator': adj.name}, code='wrong_winner',
                        ))

                # Check that the margin did not exceed the maximum permissible.
                margin = abs(totals[0] - totals[1])
                if self.max_margin and margin > self.max_margin:
                    self.add_error(None, forms.ValidationError(
                        _("The margin (%(margin).1f) in the ballot of adjudicator %(adjudicator)s exceeds the maximum allowable margin (%(max_margin).1f)."),
                        params={'adjudicator': adj.name, 'margin': margin, 'max_margin': self.max_margin}, code='max_margin',
                    ))

    def populate_result_with_scores(self, result):
        for adj in self.adjudicators:
            for side, pos in product(self.sides, self.positions):
                score = self.cleaned_data[self._fieldname_score(adj, side, pos)]
                result.set_score(adj, side, pos, score)

            if self.declared_winner not in ['none', 'high-points']:
                result.set_winners(adj, set([self.cleaned_data.get(self._fieldname_declared_winner(adj))]))

    # --------------------------------------------------------------------------
    # Template access methods
    # --------------------------------------------------------------------------

    def scoresheets(self):
        """Generates a sequence of nested dicts that allows for easy iteration
        through the form. Used in the ballot_set.html template."""
        for adj in self.adjudicators:
            sheet_dict = {
                "adjudicator": adj,
                "teams": self.scoresheet(
                    lambda side, pos: self._fieldname_score(adj, side, pos),
                ),
            }
            if self.using_declared_winner:
                sheet_dict['declared_winner'] = self[self._fieldname_declared_winner(adj)]
            yield sheet_dict


class TeamsMixin:
    """Provides a multiple-select (checkbox) of the teams for scoreless ballots."""

    has_scores = False

    def create_participant_fields(self):
        self.create_score_fields()

    def create_team_selector(self):
        # 3(a). List of teams in multiple-select
        side_choices = [(side, _("%(team)s (%(side)s)") % {
            'team': self.debate.get_team(side).short_name,
            'side': self._side_name(side)}) for side in self.tournament.sides]
        return forms.MultipleChoiceField(choices=side_choices,
                widget=forms.CheckboxSelectMultiple)

    def initial_from_result(self, result):
        return {}

    def clean(self):
        cleaned_data = super().clean()

        if not self.debate.sides_confirmed:
            self.add_error(None, forms.ValidationError(
                _("Sides for this debate are not confirmed. You can't save a result "
                  "for this debate until the sides have been confirmed in the draw."),
                code='sides_unconfirmed',
            ))

        return cleaned_data

    def save_participant_fields(self, result):
        self.populate_result_with_wins(result)

    def list_participant_fields(self):
        return []


class SingleEliminationBallotSetForm(TeamsMixin, BaseBallotSetForm):

    result_class = ConsensusDebateResult

    @staticmethod
    def _fieldname_advancing():
        return 'advancing'

    def create_score_fields(self):
        """Adds the speaker score fields:
         - <side>_score_s#,  one for each score
        """
        self.fields[self._fieldname_advancing()] = self.create_team_selector()

    def list_score_fields(self):
        return [self._fieldname_advancing()]

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)
        initial[self._fieldname_advancing()] = list(result.get_winner())
        return initial

    def clean(self):
        cleaned_data = super().clean()

        num_advancing = 2 if self.tournament.pref('teams_in_debate') == 'bp' and not self.debate.round.is_last else 1
        if self._fieldname_advancing() in cleaned_data and len(cleaned_data[self._fieldname_advancing()]) != num_advancing:
            self.add_error(self._fieldname_advancing(), forms.ValidationError(
                ngettext(
                    "There must be exactly %(n)d team advancing.",
                    "There must be exactly %(n)d teams advancing.",
                    num_advancing,
                ) % {'n': num_advancing},
                code='num_advancing',
            ))

        return cleaned_data

    def populate_result_with_wins(self, result):
        result.set_winners(set(self.cleaned_data[self._fieldname_advancing()]))

    def scoresheets(self):
        return [{'advancing': self[self._fieldname_advancing()]}]


class PerAdjudicatorEliminationBallotSetForm(TeamsMixin, BaseBallotSetForm):

    result_class = DebateResultByAdjudicator

    @staticmethod
    def _fieldname_advancing(adj):
        return 'advancing_a%(adj)d' % {'adj': adj.id}

    def create_score_fields(self):
        for adj in self.adjudicators:
            self.fields[self._fieldname_advancing(adj)] = self.create_team_selector()

    def list_score_fields(self):
        return [self._fieldname_advancing(adj) for adj in self.adjudicators]

    def initial_from_result(self, result):
        initial = super().initial_from_result(result)
        for adj in self.adjudicators:
            initial[self._fieldname_advancing(adj)] = [result.get_winner(adj)]
        return initial

    def clean(self):
        cleaned_data = super().clean()

        for adj in self.adjudicators:
            if self._fieldname_advancing(adj) in cleaned_data and len(cleaned_data[self._fieldname_advancing(adj)]) != 1:
                self.add_error(self._fieldname_advancing(adj), forms.ValidationError(
                    _("There must be exactly 1 team advancing."),
                    code='num_advancing',
                ))

    def populate_result_with_wins(self, result):
        for adj in self.adjudicators:
            result.set_winners(adj, set(self.cleaned_data[self._fieldname_advancing(adj)]))

    def scoresheets(self):
        for adj in self.adjudicators:
            yield {'advancing': self[self._fieldname_advancing(adj)]}
