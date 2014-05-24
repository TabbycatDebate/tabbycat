from django import forms
from django.utils.translation import ugettext as _

from debate.models import SpeakerScoreByAdj, Debate, Motion
from debate.models import DebateTeam, DebateAdjudicator, AdjudicatorFeedback
from debate.models import ActionLog
from debate.result import BallotSet

def get_or_instantiate(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model(**kwargs)

class ScoreField(forms.FloatField):
    MIN_VALUE = 68
    MAX_VALUE = 82

    def __init__(self, *args, **kwargs):
        if 'min_value' not in kwargs:
            kwargs['min_value'] = self.MIN_VALUE
        if 'max_value' not in kwargs:
            kwargs['max_value'] = self.MAX_VALUE
        super(ScoreField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(ScoreField, self).validate(value)
        self.check_value(value)

    def check_value(self, value):
        if int(value) != value:
            raise forms.ValidationError(
                _('Please enter a whole number.'), code='decimal'
            )

class ReplyScoreField(ScoreField):
    MIN_VALUE = 34
    MAX_VALUE = 41

    def check_value(self, value):
        if value % 0.5 != 0:
            raise forms.ValidationError(
                _('Please enter a multiple of 0.5'), code='decimal'
            )

class BallotSetForm(forms.Form):
    """Form for data entry for a single set of ballots.
    Responsible for presenting the part that looks like a ballot, i.e.
    speaker names and scores for each adjudicator. Not responsible for
    controls that submit the form or anything like that.
    """

    confirmed = forms.BooleanField(
        widget = forms.Select(attrs = {'tabindex': 100}))
    discarded = forms.BooleanField(
        widget = forms.Select(attrs = {'tabindex': 101}))

    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES,
        widget = forms.Select(attrs = {'tabindex': 102}))

    def __init__(self, ballots, *args, **kwargs):
        """
        Dynamically generate fields for this debate

        <side>_speaker_<pos> and
        <side>_score_<pos>
        """
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicators = self.debate.adjudicators.list

        super(BallotSetForm, self).__init__(*args, **kwargs)

        # Grab info about how many positions there are
        tournament = self.debate.round.tournament
        self.POSITIONS = tournament.POSITIONS
        self.LAST_SUBSTANTIVE_POSITION = tournament.LAST_SUBSTANTIVE_POSITION
        self.REPLY_POSITION = tournament.REPLY_POSITION

        # Limit the motions you can choose to the motions for this round
        motions = self.debate.round.motion_set
        self.show_motion = motions.exists() # this is used in the template
        self.initial = self._initial_data()

        # Grab the relevant score field configurations
        config = tournament.config
        score_kwargs = dict(min_value = config.get('score_min'), max_value = config.get('score_max'))
        reply_score_kwargs = dict(min_value = config.get('reply_score_min'), max_value = config.get('reply_score_max'))

        # Select the motion first if there's more than one, or last (after the save button)
        # if there's only one.  (This isn't shown if there are no motions.)
        self.fields['motion'] = forms.ModelChoiceField(
            queryset = motions,
            widget   = forms.Select(attrs = {'tabindex': motions.count() > 1 and 1 or 200}),
            required = False)

        # tab indices are as follows (example):
        #
        # Adjudicator 1
        #  21 A1name  22 A1score    29 N1name  30 N1score
        #  23 A2name  24 A2score    31 N2name  32 N2score
        #  25 A3name  26 A3score    33 N3name  34 N3score
        #  27 ARname  28 ARscore    35 NRname  36 NRscore
        #
        # Adjudicator 2 (odd numbers not used)
        #   - A1name  38 A1score     - N1name  46 N1score
        #   - A2name  40 A2score     - N2name  48 N2score
        #   - A3name  42 A3score     - N3name  50 N3score
        #   - ARname  44 ARscore     - NRname  52 NRscore
        #
        # Adjudicator 3 (odd numbers not used)
        #   - A1name  54 A1score     - N1name  62 N1score
        #   - A2name  56 A2score     - N2name  64 N2score
        #   - A3name  58 A3score     - N3name  66 N3score
        #   - ARname  60 ARscore     - NRname  68 NRscore

        MAX_POSITION = max(self.POSITIONS)

        for side, tab_index_add in (('aff', 0), ('neg', 2 * MAX_POSITION)):
            team = self.debate.get_team(side)
            for pos in self.POSITIONS:
                self.fields['%s_speaker_%s' % (side, pos)] = forms.ModelChoiceField(
                    queryset = team.speakers,
                    widget = forms.Select(attrs = {
                        'tabindex': 19 + 2 * pos + tab_index_add
                    }))

                # css_class is for jquery validation plugin, surely this can
                # be moved elsewhere
                if pos == self.REPLY_POSITION:
                    score_field = ReplyScoreField
                    kwargs = reply_score_kwargs
                    css_class = 'required number'
                else:
                    score_field = ScoreField
                    kwargs = score_kwargs
                    css_class = 'required number'

                for i, adj in enumerate(self.adjudicators):
                    self.fields[self.score_field_name(adj, side, pos)] = score_field(
                        widget = forms.TextInput(attrs={
                            'class': css_class,
                            'tabindex': 20 + 2 * pos + tab_index_add + 4 * MAX_POSITION * i
                        }), **kwargs)

    def score_field_name(self, adj, side, pos):
        """
        Return the name of the score field for adj/side/pos
        """
        return '%s_score_a%d_%d' % (side, adj.id, pos)

    def score_field(self, adj, side, pos):
        return self[self.score_field_name(adj, side, pos)]

    def _initial_data(self):
        """
        Generate dictionary of initial form data
        """

        initial = {'debate_result_status': self.debate.result_status,
            'confirmed': self.ballots.confirmed,
            'discarded': self.ballots.discarded}

        bs = BallotSet(self.ballots)

        # This isn't relevant if we're not showing the motions field
        # (i.e. there are no motions given for this round).
        # Generally, initialise the motion to what is currently in the
        # database.  But if there is only one motion and no motion is
        # currently stored in the database for this round, then default
        # to the only motion there is.
        motions = self.debate.round.motion_set
        if self.show_motion:
            if not bs.motion and motions.count() == 1:
                initial['motion'] = motions[0]
            else:
                initial['motion'] = bs.motion

        for side in ('aff', 'neg'):
            for i in self.POSITIONS:
                speaker = bs.get_speaker(side, i)
                if speaker:
                    initial['%s_speaker_%d' % (side, i)] = speaker.id

                    for adj in self.adjudicators:
                        score = bs.get_score(adj, side, i)
                        initial[self.score_field_name(adj, side, i)] = score

        return initial

    def clean(self):
        cleaned_data = super(BallotSetForm, self).clean()

        errors = list()

        for adj in self.adjudicators:
            # Check that it was not a draw
            try:
                aff_total = sum(cleaned_data[self.score_field_name(adj, 'aff', pos)] for pos in self.POSITIONS)
                neg_total = sum(cleaned_data[self.score_field_name(adj, 'neg', pos)] for pos in self.POSITIONS)
            except KeyError:
                continue
            if aff_total == neg_total:
                errors.append(forms.ValidationError(
                    _('The total scores for the teams are the same (i.e. a draw) for adjudicator %(adj)s (%(adj_ins)s)'),
                    params={'adj': adj.name, 'adj_ins': adj.institution.code}, code='draw'
                ))

        # The third speaker can't give the reply.
        for side in ('affirmative', 'negative'):
            try:
                reply_speaker_error = cleaned_data['%s_speaker_%d' % (side[:3], self.LAST_SUBSTANTIVE_POSITION)] == cleaned_data['%s_speaker_%d' % (side[:3], self.REPLY_POSITION)]
            except KeyError:
                continue
            if reply_speaker_error:
                errors.append(forms.ValidationError(
                    _('The last substantive speaker and reply speaker for the %(side)s team are the same.'),
                    params={'side': side}, code='reply_speaker'
                ))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def save(self):
        bs = BallotSet(self.ballots)

        bs.set_motion(self.cleaned_data['motion'])
        def do(side):
            for i in self.POSITIONS:
                speaker = self.cleaned_data['%s_speaker_%d' % (side, i)]
                bs.set_speaker(side, i, speaker)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self.score_field_name(adj, side, i)]
                    bs.set_score(adj, side, i, score)
        do('aff')
        do('neg')

        bs.save()

        self.ballots.discarded = self.cleaned_data['discarded']
        self.ballots.confirmed = self.cleaned_data['confirmed']

        # Unconfirm the other, if necessary
        if self.ballots.confirmed:
            if self.debate.confirmed_ballot != self.ballots:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        self.ballots.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

    def adj_iter(self):
        form = self

        class Position(object):
            def __init__(self, adj, pos, name):
                self.adj = adj
                self.pos = pos
                self.name = name

            def __unicode__(self):
                return unicode(self.name)

            def aff_speaker(self):
                return form['aff_speaker_%d' % self.pos]

            def neg_speaker(self):
                return form['neg_speaker_%d' % self.pos]

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
                    name = (i == form.REPLY_POSITION) and "Reply" or str(i)
                    yield Position(self.adj, i, name)


        for adj in self.adjudicators:
            yield AdjudicatorWrapper(adj)


def make_feedback_form_class(adjudicator):

    debates = [da.debate for da in DebateAdjudicator.objects.filter(
        adjudicator = adjudicator )]

    def adj_choice(da):
        return (
            'A:%d' % da.id,
            '%s (%d, %s)' % (da.adjudicator.name, da.debate.round.seq,
                           da.type)
        )

    adj_choices = [(None, '-- Adjudicators --')]
    adj_choices.extend ([
        adj_choice(da) for da in DebateAdjudicator.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate') if da.adjudicator != adjudicator
    ])

    if len(adj_choices) == 1: adj_choices = []

    def team_choice(dt):
        return (
            'T:%d' % dt.id,
            '%s (%d)' % (dt.team.name, dt.debate.round.seq)
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
            return DebateAdjudicator.objects.get(pk=id)
        if obj_type.strip() == 'T':
            return DebateTeam.objects.get(pk=id)

    class FeedbackForm(forms.Form):
        source = forms.TypedChoiceField(
            choices = choices,
            #coerce = coerce, # This seems to mess up data cleaning?
        )

        score = forms.FloatField(
            min_value = 0,
            max_value = 5,
        )

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            source = self.cleaned_data['source']
            source = coerce(source)

            if isinstance(source, DebateAdjudicator):
                sa = source
            else:
                sa = None
            if isinstance(source, DebateTeam):
                st = source
            else:
                st = None

            try:
                af = AdjudicatorFeedback.objects.get(
                    adjudicator = adjudicator,
                    source_adjudicator = sa,
                    source_team = st,
                )
            except AdjudicatorFeedback.DoesNotExist:
                af = AdjudicatorFeedback(
                    adjudicator = adjudicator,
                    source_adjudicator = sa,
                    source_team = st,
                )

            af.score = self.cleaned_data['score']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm


def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))


