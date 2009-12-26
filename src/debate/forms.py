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
    
    aff_speakers = debate.aff_team.speakers
    neg_speakers = debate.neg_team.speakers

    aff_initial = initial(debate, debate.aff_team)
    neg_initial = initial(debate, debate.neg_team)

    class ResultForm(forms.Form):

        result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES)

        aff_speaker_1 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[1])
        aff_speaker_2 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[2])
        aff_speaker_3 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[3])
        aff_speaker_4 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[4])

        neg_speaker_1 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[1])
        neg_speaker_2 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[2])
        neg_speaker_3 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[3])
        neg_speaker_4 = forms.ModelChoiceField(queryset=neg_speakers,
                                                   initial=neg_initial[4])

        aff_score_1 = ScoreField()
        aff_score_2 = ScoreField()
        aff_score_3 = ScoreField()
        aff_score_4 = ReplyScoreField()

        neg_score_1 = ScoreField()
        neg_score_2 = ScoreField()
        neg_score_3 = ScoreField()
        neg_score_4 = ReplyScoreField()

        def __init__(self, *args, **kwargs):
            super(ResultForm, self).__init__(*args, **kwargs)
            self.debate = debate

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

    return ResultForm

def make_results_form(debate):
    class_ = make_results_form_class(debate)
    result = DebateResult(debate)
    initial = { 'result_status': debate.result_status }
    for side in ('aff', 'neg'):
        for i in range(1, 5):
            s = getattr(result, '%s_speaker_%d' % (side, i))
            if s:
                initial['%s_speaker_%d' % (side, i)] = s.id
                initial['%s_score_%d' % (side, i)] = s.score

    return class_(initial=initial)

