from django import forms

from debate.models import TeamScoreSheet, SpeakerScoreSheet, DebateResult, Debate

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

        def aff_score_iter(self):
            for i, adj in enumerate(self.form.debate.adjudicators):
                yield self.form['aff_%d_score_%d' % (self.pos, i)]

        def neg_score_iter(self):
            for i, adj in enumerate(self.form.debate.adjudicators):
                yield self.form['neg_%d_score_%d' % (self.pos, i)]

    
    class ResultFormMetaclass(forms.Form.__metaclass__):
        def __new__(cls, name, bases, attrs):

            attrs['debate'] = debate
            adjudicators = tuple(a for t, a in debate.adjudicators)
            attrs['adjudicators'] = adjudicators

            # create speaker fields
            for side in ('aff', 'neg'):
                team = debate.get_team(side)
                init = initial(debate, team)
                for i in range(1, 5):
                    attrs['%s_speaker_%s' % (side, i)] = forms.ModelChoiceField(
                        queryset = team.speakers,
                        initial = init[i],
                    )

                    if i == 4:
                        score_field = ReplyScoreField
                    else:
                        score_field = ScoreField

                    # create score fields
                    for j in range(len(adjudicators)):
                        attrs['%s_%d_score_%d' % (side, i, j)] = score_field()


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
                total = sum(self.cleaned_data['%s_score_%d' % (side, i)] for i
                            in range(1, 5)) 
                setattr(dr, '%s_score' % side, total)

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

            #TODO
            continue
            s = result.debate.get_speaker(side, i)
            if s:
                initial['%s_speaker_%d' % (side, i)] = s.id
                initial['%s_score_%d' % (side, i)] = s.score

    return class_(initial=initial)

def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))

