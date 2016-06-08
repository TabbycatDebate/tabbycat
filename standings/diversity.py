from django.db.models import Avg, Q

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
        count = queryset.values_list(term, flat=True).order_by(term)[int(round(count / 2))]
        return count
    else:
        return None


def get_diversity_data_sets(t):

    data_sets = {
        'speakers_gender': [],
        'speakers_results': [],
        'adjudicators_gender': [],
        'adjudicators_positions': [],
        'adjudicators_results': [],
    }

    # ==========================================================================
    # Speakers Demographics
    # ==========================================================================

    data_sets['speakers_gender'].append(package_data_set('All Speakers', **{
        'Male':     Speaker.objects.filter(team__tournament=t).filter(gender=Person.GENDER_MALE).count(),
        'NM':       Speaker.objects.filter(team__tournament=t).filter(
            Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).count(),
        'Unknown':  Speaker.objects.filter(team__tournament=t).filter(gender=None).count(),
    }))

    if Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False).count() > 0:
        data_sets['speakers_gender'].append(package_data_set('Breaking', **{
            'Male':     Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False, gender=Person.GENDER_MALE).count(),
            'NM':       Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False).filter(
                Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).count(),
            'Unknown':  Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False, gender=None).count(),
        }))

    if Speaker.objects.filter(team__tournament=t).filter(novice=True).count() > 0:
        data_sets['speakers_gender'].append(package_data_set('Pros', **{
            'Male':     Speaker.objects.filter(team__tournament=t).filter(novice=False, gender=Person.GENDER_MALE).count(),
            'NM':       Speaker.objects.filter(team__tournament=t).filter(novice=False).filter(
                Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).count(),
            'Unknown':  Speaker.objects.filter(team__tournament=t).filter(novice=False, gender=None).count(),
        }))
        data_sets['speakers_gender'].append(package_data_set('Novices', **{
            'Male':     Speaker.objects.filter(team__tournament=t).filter(novice=True, gender=Person.GENDER_MALE).count(),
            'NM':       Speaker.objects.filter(team__tournament=t).filter(novice=True).filter(
                Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).count(),
            'Unknown':  Speaker.objects.filter(team__tournament=t).filter(novice=True, gender=None).count(),
        }))

    # ==========================================================================
    # Adjudicators Demographics
    # ==========================================================================

    data_sets['adjudicators_gender'].append(package_data_set('All Adjudicators', **{
        'Male':     Adjudicator.objects.filter(tournament=t).filter(
            gender=Person.GENDER_MALE).count(),
        'NM':       Adjudicator.objects.filter(tournament=t).filter(
            Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).count(),
        'Unknown':  Adjudicator.objects.filter(tournament=t).filter(
            gender=None).count()
    }))

    if Adjudicator.objects.filter(tournament=t).filter(independent=True).count() > 0:
        data_sets['adjudicators_gender'].append(package_data_set('Independents', **{
            'Male':     Adjudicator.objects.filter(tournament=t).filter(
                gender=Person.GENDER_MALE, independent=True).count(),
            'NM':       Adjudicator.objects.filter(tournament=t).filter(
                Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).filter(independent=True).count(),
            'Unknown':  Adjudicator.objects.filter(tournament=t).filter(
                gender=None, independent=True).count()
        }))

    if Adjudicator.objects.filter(breaking=True).count() > 0:
        data_sets['adjudicators_gender'].append(package_data_set('Breaking', **{
            'Male':     Adjudicator.objects.filter(tournament=t).filter(
                gender=Person.GENDER_MALE, breaking=True).count(),
            'NM':       Adjudicator.objects.filter(tournament=t).filter(
                Q(gender=Person.GENDER_FEMALE) | Q(gender=Person.GENDER_OTHER)).filter(breaking=True).count(),
            'Unknown':  Adjudicator.objects.filter(tournament=t).filter(
                gender=None, breaking=True).count()
        }))

    data_sets['adjudicators_positions'].append(package_data_set('Chairs', **{
        'Male':     DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_CHAIR).count(),
        'NM':       DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            Q(adjudicator__gender=Person.GENDER_FEMALE) | Q(adjudicator__gender=Person.GENDER_OTHER)).filter(type=DebateAdjudicator.TYPE_CHAIR).count(),
        'Unknown':  DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=None, type=DebateAdjudicator.TYPE_CHAIR).count()
    }))
    data_sets['adjudicators_positions'].append(package_data_set('Panellists', **{
        'Male':     DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_PANEL).count(),
        'NM':       DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            Q(adjudicator__gender=Person.GENDER_FEMALE) | Q(adjudicator__gender=Person.GENDER_OTHER)).filter(type=DebateAdjudicator.TYPE_PANEL).count(),
        'Unknown':  DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=None, type=DebateAdjudicator.TYPE_PANEL).count()
    }))
    data_sets['adjudicators_positions'].append(package_data_set('Trainees', **{
        'Male':     DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=Person.GENDER_MALE, type=DebateAdjudicator.TYPE_TRAINEE).count(),
        'NM':       DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            Q(adjudicator__gender=Person.GENDER_FEMALE) | Q(adjudicator__gender=Person.GENDER_OTHER)).filter(type=DebateAdjudicator.TYPE_TRAINEE).count(),
        'Unknown':  DebateAdjudicator.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=None, type=DebateAdjudicator.TYPE_TRAINEE).count()
    }))

    # ==========================================================================
    # Adjudicators Results
    # ==========================================================================

    overall = AdjudicatorFeedback.objects.filter(adjudicator__tournament=t).aggregate(Avg('score'))['score__avg']
    data_sets['adjudicators_results'].append(package_data_set('Average Rating', **{
        'Male':     AdjudicatorFeedback.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=Person.GENDER_MALE).aggregate(Avg('score'))['score__avg'] - overall,
        'NaOverall':  overall,
        'NM':       AdjudicatorFeedback.objects.filter(adjudicator__tournament=t).filter(
            Q(adjudicator__gender=Person.GENDER_FEMALE) | Q(adjudicator__gender=Person.GENDER_OTHER)).aggregate(Avg('score'))['score__avg'] - overall
    }))

    overall = median_value(AdjudicatorFeedback.objects.filter(adjudicator__tournament=t), 'score')
    data_sets['adjudicators_results'].append(package_data_set('Median Rating', **{
        'Male':     median_value(AdjudicatorFeedback.objects.filter(adjudicator__tournament=t).filter(
            adjudicator__gender=Person.GENDER_MALE), 'score') - overall,
        'NaOverall':overall,
        'NM':       median_value(AdjudicatorFeedback.objects.filter(adjudicator__tournament=t).filter(
            Q(adjudicator__gender=Person.GENDER_FEMALE) | Q(adjudicator__gender=Person.GENDER_OTHER)), 'score') - overall
    }))

    # ==========================================================================
    # Speakers Results
    # ==========================================================================

    overall = SpeakerScore.objects.filter(speaker__team__tournament=t).aggregate(Avg('score'))['score__avg']
    data_sets['speakers_results'].append(package_data_set('Average Score', **{
        'Male':     SpeakerScore.objects.filter(speaker__team__tournament=t).filter(
            speaker__gender=Person.GENDER_MALE).aggregate(Avg('score'))['score__avg'] - overall,
        'Overall':  overall,
        'NM':       SpeakerScore.objects.filter(speaker__team__tournament=t).filter(
            Q(speaker__gender=Person.GENDER_FEMALE) | Q(speaker__gender=Person.GENDER_OTHER)).aggregate(Avg('score'))['score__avg'] - overall
    }))

    overall = median_value(SpeakerScore.objects.filter(speaker__team__tournament=t), 'score')
    data_sets['speakers_results'].append(package_data_set('Median Score', **{
        'Male':     median_value(SpeakerScore.objects.filter(speaker__team__tournament=t).filter(
            speaker__gender=Person.GENDER_MALE), 'score') - overall,
        'Overall':  overall,
        'NM':       median_value(SpeakerScore.objects.filter(speaker__team__tournament=t).filter(
            Q(speaker__gender=Person.GENDER_FEMALE) | Q(speaker__gender=Person.GENDER_OTHER)), 'score') - overall,
    }))

    return data_sets
