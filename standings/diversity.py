from django.db.models import Avg

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from participants.models import Adjudicator, Person, Speaker, Team
from results.models import SpeakerScore, TeamScore


def package_data_set():

    data_set = {
        'title': 'All Speakers',
        'data': [
            {'Male': 45},
            {'Female': 40},
            {'Other': 10},
            {'Unknown': 2}
        ]
    }

    return data_set


def median_value(queryset, term):
    count = queryset.count()
    return queryset.values_list(term, flat=True).order_by(term)[int(round(count / 2))]


def get_data_sets():

    kwargs = {}

    kwargs['speakers_m'] = Speaker.objects.filter(
        gender=Person.GENDER_MALE).count()
    kwargs['speakers_f'] = Speaker.objects.filter(
        gender=Person.GENDER_FEMALE).count()
    kwargs['speakers_o'] = Speaker.objects.filter(
        gender=Person.GENDER_OTHER).count()
    kwargs['speakers_u'] = Speaker.objects.filter(
        gender=None).count()

    kwargs['bspeakers_m'] = Speaker.objects.filter(
        team__breakingteam__isnull=False, gender=Person.GENDER_MALE).count()
    kwargs['bspeakers_f'] = Speaker.objects.filter(
        team__breakingteam__isnull=False, gender=Person.GENDER_FEMALE).count()
    kwargs['bspeakers_o'] = Speaker.objects.filter(
        team__breakingteam__isnull=False, gender=Person.GENDER_OTHER).count()
    kwargs['bspeakers_u'] = Speaker.objects.filter(
        team__breakingteam__isnull=False, gender=None).count()

    kwargs['pspeakers_m'] = Speaker.objects.filter(
        novice=False, gender=Person.GENDER_MALE).count()
    kwargs['pspeakers_f'] = Speaker.objects.filter(
        novice=False, gender=Person.GENDER_FEMALE).count()
    kwargs['pspeakers_o'] = Speaker.objects.filter(
        novice=False, gender=Person.GENDER_OTHER).count()
    kwargs['pspeakers_u'] = Speaker.objects.filter(
        novice=False, gender=None).count()

    kwargs['nspeakers_m'] = Speaker.objects.filter(
        novice=True, gender=Person.GENDER_MALE).count()
    kwargs['nspeakers_f'] = Speaker.objects.filter(
        novice=True, gender=Person.GENDER_FEMALE).count()
    kwargs['nspeakers_o'] = Speaker.objects.filter(
        novice=True, gender=Person.GENDER_OTHER).count()
    kwargs['nspeakers_u'] = Speaker.objects.filter(
        novice=True, gender=None).count()

    kwargs['adjs_m'] = Adjudicator.objects.filter(
        gender=Person.GENDER_MALE).count()
    kwargs['adjs_f'] = Adjudicator.objects.filter(
        gender=Person.GENDER_FEMALE).count()
    kwargs['adjs_o'] = Adjudicator.objects.filter(
        gender=Person.GENDER_OTHER).count()
    kwargs['adjs_u'] = Adjudicator.objects.filter(
        gender=None).count()

    kwargs['badjs_m'] = Adjudicator.objects.filter(
        gender=Person.GENDER_MALE, breaking=True).count()
    kwargs['badjs_f'] = Adjudicator.objects.filter(
        gender=Person.GENDER_FEMALE, breaking=True).count()
    kwargs['badjs_o'] = Adjudicator.objects.filter(
        gender=Person.GENDER_OTHER, breaking=True).count()
    kwargs['badjs_u'] = Adjudicator.objects.filter(
        gender=None, breaking=True).count()

    kwargs['iadjs_m'] = Adjudicator.objects.filter(
        gender=Person.GENDER_MALE, independent=True).count()
    kwargs['iadjs_f'] = Adjudicator.objects.filter(
        gender=Person.GENDER_FEMALE, independent=True).count()
    kwargs['iadjs_o'] = Adjudicator.objects.filter(
        gender=Person.GENDER_OTHER, independent=True).count()
    kwargs['iadjs_u'] = Adjudicator.objects.filter(
        gender=None, independent=True).count()

    kwargs['aadjs_m'] = Adjudicator.objects.filter(
        gender=Person.GENDER_MALE, adj_core=True).count()
    kwargs['aadjs_f'] = Adjudicator.objects.filter(
        gender=Person.GENDER_FEMALE, adj_core=True).count()
    kwargs['aadjs_o'] = Adjudicator.objects.filter(
        gender=Person.GENDER_OTHER, adj_core=True).count()
    kwargs['aadjs_u'] = Adjudicator.objects.filter(
        gender=None, adj_core=True).count()

    kwargs['chair_adjs_m'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_CHAIR).count()
    kwargs['chair_adjs_f'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_FEMALE, type=DebateAdjudicator.TYPE_CHAIR).count()
    kwargs['chair_adjs_o'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_OTHER, type=DebateAdjudicator.TYPE_CHAIR).count()
    kwargs['chair_adjs_u'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=None, type=DebateAdjudicator.TYPE_CHAIR).count()

    kwargs['panel_adjs_m'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_PANEL).count()
    kwargs['panel_adjs_f'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_FEMALE, type=DebateAdjudicator.TYPE_PANEL).count()
    kwargs['panel_adjs_o'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_OTHER, type=DebateAdjudicator.TYPE_PANEL).count()
    kwargs['panel_adjs_u'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=None, type=DebateAdjudicator.TYPE_PANEL).count()

    kwargs['trainee_adjs_m'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_TRAINEE).count()
    kwargs['trainee_adjs_f'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_FEMALE, type=DebateAdjudicator.TYPE_TRAINEE).count()
    kwargs['trainee_adjs_o'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=Person.GENDER_OTHER, type=DebateAdjudicator.TYPE_TRAINEE).count()
    kwargs['trainee_adjs_u'] = DebateAdjudicator.objects.filter(
        adjudicator__gender=None, type=DebateAdjudicator.TYPE_TRAINEE).count()

    kwargs['m_avg_speak'] = SpeakerScore.objects.filter(
        speaker__gender=Person.GENDER_MALE).aggregate(Avg('score'))
    kwargs['f_avg_speak'] = SpeakerScore.objects.filter(
        speaker__gender=Person.GENDER_FEMALE).aggregate(Avg('score'))

    kwargs['m_avg_rating'] = AdjudicatorFeedback.objects.filter(
        adjudicator__gender=Person.GENDER_MALE).aggregate(Avg('score'))
    kwargs['f_avg_rating'] = AdjudicatorFeedback.objects.filter(
        adjudicator__gender=Person.GENDER_FEMALE).aggregate(Avg('score'))

    kwargs['m_median_speak'] = median_value(SpeakerScore.objects.filter(
        speaker__gender=Person.GENDER_MALE), 'score')
    kwargs['f_median_speak'] = median_value(SpeakerScore.objects.filter(
        speaker__gender=Person.GENDER_FEMALE), 'score')

    kwargs['m_median_rating'] = median_value(AdjudicatorFeedback.objects.filter(
        adjudicator__gender=Person.GENDER_MALE), 'score')
    kwargs['f_median_rating'] = median_value(AdjudicatorFeedback.objects.filter(
        adjudicator__gender=Person.GENDER_FEMALE), 'score')

    # Stuff to do with
    print(Team)
    print(TeamScore)
