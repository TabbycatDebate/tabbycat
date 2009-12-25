from django import forms

from debate.models import TeamScoreSheet, SpeakerScoreSheet

class ScoreField(forms.IntegerField):
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
        raise
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
        aff_speaker_1 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[1])
        aff_speaker_2 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[2])
        aff_speaker_3 = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[3])
        aff_speaker_reply = forms.ModelChoiceField(queryset=aff_speakers,
                                               initial=aff_initial[4])

        neg_speaker_1 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[1])
        neg_speaker_2 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[2])
        neg_speaker_3 = forms.ModelChoiceField(queryset=neg_speakers,
                                               initial=neg_initial[3])
        neg_speaker_reply = forms.ModelChoiceField(queryset=neg_speakers,
                                                   initial=neg_initial[4])

        aff_score_1 = ScoreField()
        aff_score_2 = ScoreField()
        aff_score_3 = ScoreField()
        aff_score_reply = ReplyScoreField()

        neg_score_1 = ScoreField()
        neg_score_2 = ScoreField()
        neg_score_3 = ScoreField()
        neg_score_reply = ReplyScoreField()

        def __init__(self, *args, **kwargs):
            super(ResultForm, self).__init__(*args, **kwargs)
            self.debate = debate

        def save(self):
            #TODO: validation
            neg_dt = self.debate.neg_dt
            
            def do(team):
                dt = getattr(self.debate, '%s_dt' % team) 

                total = sum(self.cleaned_data[a] for a in 
                            ('%s_score_1' % team,
                             '%s_score_2' % team,
                             '%s_score_3' % team,
                             '%s_score_reply' % team))

                TeamScoreSheet(debate_team=dt, score=total).save()
                for i in range(1, 4):
                    SpeakerScoreSheet(
                        debate_team=dt,
                        debater=self.cleaned_data['%s_speaker_%d' % (team, i)],
                        score=self.cleaned_data['%s_score_%d' % (team, i)],
                        position=i,
                    ).save()
            do('aff')
            do('neg')

    return ResultForm

def make_results_form(debate):
    class_ = make_results_form_class(debate)
    return class_()

