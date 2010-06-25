from django import forms

from debate.models import SpeakerScoreByAdj, DebateResult, Debate
from debate.models import DebateTeam, DebateAdjudicator, AdjudicatorFeedback
from debate.result import DebateResult

def get_or_instantiate(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model(**kwargs)

class ScoreField(forms.FloatField):
    MIN_VALUE = 60
    MAX_VALUE = 80

    def __init__(self, *args, **kwargs):
        if 'min_value' not in kwargs:
            kwargs['min_value'] = self.MIN_VALUE
        if 'max_value' not in kwargs:
            kwargs['max_value'] = self.MAX_VALUE
        super(ScoreField, self).__init__(*args, **kwargs)

class ReplyScoreField(ScoreField):
    MIN_VALUE = 30
    MAX_VALUE = 40

class ResultForm(forms.Form):

    result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

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

        for side in ('aff', 'neg'):
            team = debate.get_team(side)
            for pos in range(1, 5):
                self.fields['%s_speaker_%s' % (side, pos)] = forms.ModelChoiceField(
                    queryset = team.speakers,
                )

                # css_class is for jquery validation plugin, surely this can
                # be moved elsewhere
                if pos == 4:
                    score_field = ReplyScoreField
                    css_class = 'required number'
                else:
                    score_field = ScoreField
                    css_class = 'required number'

                for adj in self.adjudicators:
                    self.fields[self.score_field_name(adj, side, pos)] = score_field(
                        widget = forms.TextInput(attrs={'class': css_class}))

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

        initial = {'result_status': self.debate.result_status}
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


    def save(self):
        #TODO: validation

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
            '(%d) %s' % (da.debate.round.seq, da.adjudicator.name)
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
            '(%d) %s' % (dt.debate.round.seq, dt.team.name)
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

            a, c = AdjudicatorFeedback.objects.get_or_create(
                adjudicator = adjudicator,
                source_adjudicator = sa,
                source_team = st,
            )
            a.score = self.cleaned_data['score']
            a.comments = self.cleaned_data['comment']

            a.save()



    return FeedbackForm


def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))


