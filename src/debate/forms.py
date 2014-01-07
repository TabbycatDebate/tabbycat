from django import forms
from django.utils.translation import ugettext as _

from debate.models import SpeakerScoreByAdj, DebateResult, Debate, Motion
from debate.models import DebateTeam, DebateAdjudicator, AdjudicatorFeedback
from debate.result import DebateResult

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

class ResultForm(forms.Form):

    result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES,
        widget = forms.Select(attrs = {'tabindex': 100}))

    def __init__(self, debate, *args, **kwargs):
        """
        Dynamically generate fields for this debate

        <side>_speaker_<pos> and
        <side>_score_<pos>
        """
        self.debate = debate
        self.adjudicators = debate.adjudicators.list

        super(ResultForm, self).__init__(*args, **kwargs)

        self.initial = self._initial_data()

        self.fields['motion'] = forms.ModelChoiceField(
            queryset = Motion.objects.filter(round=self.debate.round),
            widget = forms.Select(attrs = {'tabindex': 0}))

        # tab indices are as follows:
        #
        # Adjudicator 1
        #  1 A1name  2 A1score     9 N1name  10 N1score
        #  3 A2name  4 A2score    11 N2name  12 N2score
        #  5 A3name  6 A3score    13 N3name  14 N3score
        #  7 ARname  8 ARscore    15 NRname  16 NRscore
        #
        # Adjudicator 2 (odd numbers not used)
        #  - A1name 18 A1score     - N1name  26 N1score
        #  - A2name 20 A2score     - N2name  28 N2score
        #  - A3name 22 A3score     - N3name  30 N3score
        #  - ARname 24 ARscore     - NRname  32 NRscore
        #
        # Adjudicator 3 (odd numbers not used)
        #  - A1name 34 A1score     - N1name  42 N1score
        #  - A2name 36 A2score     - N2name  44 N2score
        #  - A3name 38 A3score     - N3name  46 N3score
        #  - ARname 40 ARscore     - NRname  48 NRscore

        for side in ('aff', 'neg'):
            team = debate.get_team(side)
            for pos in range(1, 5):
                self.fields['%s_speaker_%s' % (side, pos)] = forms.ModelChoiceField(
                    queryset = team.speakers,
                    widget = forms.Select(attrs = {
                        'tabindex': 2 * pos + (side == 'neg' and 7 or -1)
                    }))

                # css_class is for jquery validation plugin, surely this can
                # be moved elsewhere
                if pos == 4:
                    score_field = ReplyScoreField
                    css_class = 'required number'
                else:
                    score_field = ScoreField
                    css_class = 'required number'

                for i, adj in enumerate(self.adjudicators):
                    self.fields[self.score_field_name(adj, side, pos)] = score_field(
                        widget = forms.TextInput(attrs={
                            'class': css_class,
                            'tabindex': 2 * pos + (side == 'neg' and 8 or 0) + 16 * i
                        }))

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

        initial = {'result_status': self.debate.result_status, 'motion': self.debate.motion}
        result = self.debate.result

        for side in ('aff', 'neg'):
            for i in range(1, 5):
                speaker = result.get_speaker(side, i)
                if speaker:
                    initial['%s_speaker_%d' % (side, i)] = speaker.id

                    for adj in self.adjudicators:
                        score = result.get_score(adj, side, i)
                        initial[self.score_field_name(adj, side, i)] = score

        return initial

    def clean(self):
        cleaned_data = super(ResultForm, self).clean()

        errors = list()

        for adj in self.adjudicators:
            # Check that it was not a draw
            try:
                aff_total = sum(cleaned_data[self.score_field_name(adj, 'aff', pos)] for pos in range(1, 5))
                neg_total = sum(cleaned_data[self.score_field_name(adj, 'neg', pos)] for pos in range(1, 5))
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
                reply_speaker_error = cleaned_data['%s_speaker_3' % (side[:3],)] == cleaned_data['%s_speaker_4' % (side[:3],)]
            except KeyError:
                continue
            if reply_speaker_error:
                errors.append(forms.ValidationError(
                    _('The third speaker and reply speaker for the %(side)s team are the same.'),
                    params={'side': side}, code='reply_speaker'
                ))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def save(self):
        dr = DebateResult(self.debate)

        def do(side):
            for i in range(1, 5):
                speaker = self.cleaned_data['%s_speaker_%d' % (side, i)]
                dr.set_speaker(side, i, speaker)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self.score_field_name(adj, side, i)]
                    dr.set_score(adj, side, i, score)
        do('aff')
        do('neg')
        dr.save()

        self.debate.result_status = self.cleaned_data['result_status']
        self.debate.motion = self.cleaned_data['motion']
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
                for i, name in ((1, 1), (2, 2), (3, 3), (4, 'Reply')):
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
            coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 0,
            max_value = 5,
        )

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def save(self):
            source = self.cleaned_data['source']
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

    return FeedbackForm


def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))


