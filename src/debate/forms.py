from django import forms

from debate.models import TeamScoreSheet, SpeakerScoreSheet, DebateResult, Debate
from debate.models import DebateTeam, DebateAdjudicator, AdjudicatorFeedback

def get_or_instantiate(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model(**kwargs)

class ScoreField(forms.FloatField):
    MIN_VALUE = 65
    MAX_VALUE = 85

    def __init__(self, *args, **kwargs):
        if 'min_value' not in kwargs:
            kwargs['min_value'] = self.MIN_VALUE
        if 'max_value' not in kwargs:
            kwargs['max_value'] = self.MAX_VALUE
        super(ScoreField, self).__init__(*args, **kwargs)

class ReplyScoreField(ScoreField):
    MIN_VALUE = 30
    MAX_VALUE = 40

def initial(debate, team):
    speakers = team.speakers
    prev_debate = team.prev_debate(debate.round.seq)
    if prev_debate:
        dr = DebateResult(prev_debate)
        side = prev_debate.get_side(team)
        return dict((i, dr.get_speaker(side, i).id) for i in range(1, 5))
    else:
        return {
            1: speakers[0].id, 
            2: speakers[1].id,
            3: speakers[2].id,
            4: speakers[0].id,
        }

# TODO: must've been on something when I wrote this. get rid of the
# metaclass craziness http://www.b-list.org/weblog/2008/nov/09/dynamic-forms/ 
def make_results_form_class(debate):

    class position(object):
        def __init__(self, form, pos, name):
            self.form = form
            self.pos = pos
            self.name = name


        def __unicode__(self):
            return unicode(self.name)

        def aff_speaker(self):
            return self.form['aff_speaker_%d' % self.pos]

        def neg_speaker(self):
            return self.form['neg_speaker_%d' % self.pos]

        def aff_score(self):
            return self.form['aff_score_%d' % self.pos]

        def neg_score(self):
            return self.form['neg_score_%d' % self.pos]

    
    class ResultFormMetaclass(forms.Form.__metaclass__):
        def __new__(cls, name, bases, attrs):

            attrs['debate'] = debate

            # create speaker fields
            for side in ('aff', 'neg'):
                team = debate.get_team(side)
                init = initial(debate, team)
                for i in range(1, 5):
                    attrs['%s_speaker_%s' % (side, i)] = forms.ModelChoiceField(
                        queryset = team.speakers,
                        initial = init[i],
                    )

                    # css_class is for jquery validation plugin
                    if i == 4:
                        score_field = ReplyScoreField
                        css_class = 'required number'
                    else:
                        score_field = ScoreField
                        css_class = 'required number'

                    # create score field
                    attrs['%s_score_%d' % (side, i)] = score_field(
                        widget = forms.TextInput(attrs={'class':css_class}))


            new_class = super(ResultFormMetaclass, cls).__new__(cls, name, bases,
                                                                attrs)

            return new_class


    class ResultForm(forms.Form):

        __metaclass__ = ResultFormMetaclass

        result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

        def __init__(self, *args, **kwargs):
            super(ResultForm, self).__init__(*args, **kwargs)

        def save(self):
            #TODO: validation

            dr = DebateResult(self.debate)

            def do(side):
                for i in range(1, 5): 
                    speaker = self.cleaned_data['%s_speaker_%d' % (side, i)]
                    score = self.cleaned_data['%s_score_%d' % (side, i)]
                    dr.set_speaker_entry(side, i, speaker, score)
            do('aff')
            do('neg')
            dr.save()

            self.debate.result_status = self.cleaned_data['result_status']
            self.debate.save()

        def position_iter(self):
            for i, name in ((1, 1), (2, 2), (3, 3), (4, 'Reply')):
                yield position(self, i, name)

    return ResultForm

def make_results_form(debate):
    class_ = make_results_form_class(debate)
    result = DebateResult(debate)
    initial = { 'result_status': debate.result_status }
    for side in ('aff', 'neg'):
        for i in range(1, 5):

            sp, score = result.get_speaker_score(side, i)
            if sp:
                initial['%s_speaker_%d' % (side, i)] = sp.id
                initial['%s_score_%d' % (side, i)] = score

    return class_(initial=initial)

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

        comment = forms.CharField(widget=forms.Textarea)

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


