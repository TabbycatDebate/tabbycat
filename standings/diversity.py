from django.db.models import Avg

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from participants.models import Adjudicator, Person, Speaker
from results.models import SpeakerScore


def package_data_set(title, **kwargs):
    data_set = {'title': title, 'data': []}
    for key, value in kwargs.items():
        data_set['data'].append({'label': key, 'count': value})

    return data_set


def median_value(queryset, term):
    count = queryset.count()
    if count > 0:
        return queryset.values_list(term, flat=True).order_by(term)[int(round(count / 2))]
    else:
        return None


def get_diversity_data_sets():

    data_sets = {'speakers_gender': [], 'adjudicators_gender': []}

    values = {
        'Male':     Speaker.objects.filter(gender=Person.GENDER_MALE).count(),
        'Female':   Speaker.objects.filter(gender=Person.GENDER_FEMALE).count(),
        'Other':    Speaker.objects.filter(gender=Person.GENDER_OTHER).count(),
        'Unknown':  Speaker.objects.filter(gender=None).count(),
    }
    data_sets['speakers_gender'].append(package_data_set('All Speakers', **values))

    values = {
        'Male':     Speaker.objects.filter(team__breakingteam__isnull=False, gender=Person.GENDER_MALE).count(),
        'Female':   Speaker.objects.filter(team__breakingteam__isnull=False, gender=Person.GENDER_FEMALE).count(),
        'Other':    Speaker.objects.filter(team__breakingteam__isnull=False, gender=Person.GENDER_OTHER).count(),
        'Unknown':  Speaker.objects.filter(team__breakingteam__isnull=False, gender=None).count(),
    }
    data_sets['speakers_gender'].append(package_data_set('Breaking', **values))

    values = {
        'Male':     Speaker.objects.filter(novice=False, gender=Person.GENDER_MALE).count(),
        'Female':   Speaker.objects.filter(novice=False, gender=Person.GENDER_FEMALE).count(),
        'Other':    Speaker.objects.filter(novice=False, gender=Person.GENDER_OTHER).count(),
        'Unknown':  Speaker.objects.filter(novice=False, gender=None).count(),
    }
    data_sets['speakers_gender'].append(package_data_set('Pros', **values))

    values = {
        'Male':     Speaker.objects.filter(novice=True, gender=Person.GENDER_MALE).count(),
        'Female':   Speaker.objects.filter(novice=True, gender=Person.GENDER_FEMALE).count(),
        'Other':    Speaker.objects.filter(novice=True, gender=Person.GENDER_OTHER).count(),
        'Unknown':  Speaker.objects.filter(novice=True, gender=None).count(),
    }
    data_sets['speakers_gender'].append(package_data_set('Novices', **values))

    values = {
        'Male':     Adjudicator.objects.filter(gender=Person.GENDER_MALE).count(),
        'Female':   Adjudicator.objects.filter(gender=Person.GENDER_FEMALE).count(),
        'Other':    Adjudicator.objects.filter(gender=Person.GENDER_OTHER).count(),
        'Unknown':  Adjudicator.objects.filter(gender=None).count()
    }
    data_sets['adjudicators_gender'].append(package_data_set('All Adjudicators', **values))

    values = {
        'Male':     Adjudicator.objects.filter(gender=Person.GENDER_MALE, breaking=True).count(),
        'Female':   Adjudicator.objects.filter(gender=Person.GENDER_FEMALE, breaking=True).count(),
        'Other':    Adjudicator.objects.filter(gender=Person.GENDER_OTHER, breaking=True).count(),
        'Unknown':  Adjudicator.objects.filter(gender=None, breaking=True).count()
    }
    data_sets['adjudicators_gender'].append(package_data_set('Breaking', **values))

    values = {
        'Male':     Adjudicator.objects.filter(gender=Person.GENDER_MALE, independent=True).count(),
        'Female':   Adjudicator.objects.filter(gender=Person.GENDER_FEMALE, independent=True).count(),
        'Other':    Adjudicator.objects.filter(gender=Person.GENDER_OTHER, independent=True).count(),
        'Unknown':  Adjudicator.objects.filter(gender=None, independent=True).count()
    }
    data_sets['adjudicators_gender'].append(package_data_set('Independents', **values))

    values = {
        'Male':     Adjudicator.objects.filter(gender=Person.GENDER_MALE, adj_core=True).count(),
        'Female':   Adjudicator.objects.filter(gender=Person.GENDER_FEMALE, adj_core=True).count(),
        'Other':    Adjudicator.objects.filter(gender=Person.GENDER_OTHER, adj_core=True).count(),
        'Unknown':  Adjudicator.objects.filter(gender=None, adj_core=True).count()
    }
    data_sets['adjudicators_gender'].append(package_data_set('Adjudication Core', **values))

    kwargs = {}
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

    kwargs['m_avg_speak'] = SpeakerScore.objects.filter(speaker__gender=Person.GENDER_MALE).aggregate(Avg('score'))
    kwargs['f_avg_speak'] = SpeakerScore.objects.filter(speaker__gender=Person.GENDER_FEMALE).aggregate(Avg('score'))

    kwargs['m_avg_rating'] = AdjudicatorFeedback.objects.filter(adjudicator__gender=Person.GENDER_MALE).aggregate(Avg('score'))
    kwargs['f_avg_rating'] = AdjudicatorFeedback.objects.filter(adjudicator__gender=Person.GENDER_FEMALE).aggregate(Avg('score'))

    kwargs['m_median_speak'] = median_value(SpeakerScore.objects.filter(speaker__gender=Person.GENDER_MALE), 'score')
    kwargs['f_median_speak'] = median_value(SpeakerScore.objects.filter(speaker__gender=Person.GENDER_FEMALE), 'score')

    kwargs['m_median_rating'] = median_value(AdjudicatorFeedback.objects.filter(adjudicator__gender=Person.GENDER_MALE), 'score')
    kwargs['f_median_rating'] = median_value(AdjudicatorFeedback.objects.filter(adjudicator__gender=Person.GENDER_FEMALE), 'score')

    return data_sets
