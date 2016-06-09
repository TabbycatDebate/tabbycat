from django.db.models import Avg, Q

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from participants.models import Adjudicator, Person, Speaker
from results.models import SpeakerScore


def compile_data(title, queryset, filter_source, filters, datum=False, **kwargs):
    ''' Filter the queryset given filters and return a dictionary of results '''

    data_set = []
    for item in filters:
        [(key, value)] = item.items()  # Get the key/value pairs

        # Use keywords to filter data sets; using Q for OR conditions
        if value is not None and len(value) == 2:
            filtered = queryset.filter(Q(**{filter_source: value[0]}) | Q(**{filter_source: value[1]}))
        else:
            filtered = queryset.filter(**{filter_source: value})

        # Return a structure ready to fit the Vue template
        data_set.append({
            'label': key,
            'count': calculate_result(filtered, kwargs),
        })

    if datum is not False:  # Get the overall number to use as baseline
        datum = calculate_result(queryset, kwargs)

    return {'title': title, 'data': data_set, 'datum': datum}


def calculate_result(queryset, keywords):
    if 'count' in keywords:
        return queryset.count()
    elif 'average' in keywords:
        return queryset.aggregate(Avg('score'))['score__avg']
    elif 'median' in keywords or 'lowerq' in keywords or 'upperq' in keywords:
        ordered_values = sorted(queryset.values_list('score', flat=True))
        if 'median' in keywords:
            return median_value(ordered_values)
        elif 'lowerq' in keywords:
            return quartile(ordered_values, lower=True)
        elif 'upperq' in keywords:
            return quartile(ordered_values, upper=True)


def median_value(ordered_values):
    mid = len(ordered_values) / 2

    if (len(ordered_values) % 2 == 0):
        return (ordered_values[int(mid)-1] + ordered_values[int(mid)]) / 2.0
    else:
        return ordered_values[int(mid)]


def quartile(ordered_values, lower=False, upper=False):
    mid = len(ordered_values) / 2

    if (len(ordered_values) % 2 == 0):
        if upper:
            return median_value(ordered_values[int(mid):])
        elif lower:
            return median_value(ordered_values[:int(mid)])
    else:
        if upper:
            return median_value(ordered_values[int(mid)+1:])
        elif lower:
            return median_value(ordered_values[:int(mid)])


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

    data_sets['speakers_gender'].append(compile_data(
        'All Speakers', Speaker.objects.filter(team__tournament=t), 'gender', filters=[
            {'Unknown':  None},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
            {'Male':     Person.GENDER_MALE},
        ], count=True))

    if Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False).count() > 0:
        data_sets['speakers_gender'].append(compile_data(
            'Breaking', Speaker.objects.filter(team__tournament=t, team__breakingteam__isnull=False), 'gender', filters=[
                {'Unknown':  None},
                {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
                {'Male':     Person.GENDER_MALE},
            ], count=True))

    if Speaker.objects.filter(team__tournament=t).filter(novice=True).count() > 0:
        data_sets['speakers_gender'].append(compile_data(
            'Pros', Speaker.objects.filter(team__tournament=t, novice=False), 'gender', filters=[
                {'Unknown':  None},
                {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
                {'Male':     Person.GENDER_MALE},
            ], count=True))
        data_sets['speakers_gender'].append(compile_data(
            'Novices', Speaker.objects.filter(team__tournament=t, novice=True), 'gender', filters=[
                {'Unknown':  None},
                {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
                {'Male':     Person.GENDER_MALE},
            ], count=True))

    # ==========================================================================
    # Adjudicators Demographics
    # ==========================================================================

    data_sets['adjudicators_gender'].append(compile_data(
        'All Adjudicators', Adjudicator.objects.filter(tournament=t), 'gender', filters=[
            {'Unknown':  None},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
            {'Male':     Person.GENDER_MALE},
        ], count=True))

    if Adjudicator.objects.filter(tournament=t).filter(independent=True).count() > 0:
        data_sets['adjudicators_gender'].append(compile_data(
            'Independents', Adjudicator.objects.filter(tournament=t, independent=True), 'gender', filters=[
                {'Unknown':  None},
                {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
                {'Male':     Person.GENDER_MALE},
            ], count=True))

    if Adjudicator.objects.filter(breaking=True).count() > 0:
        data_sets['adjudicators_gender'].append(compile_data(
            'Breaking', Adjudicator.objects.filter(tournament=t, breaking=True), 'gender', filters=[
                {'Unknown':  None},
                {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
                {'Male':     Person.GENDER_MALE},
            ], count=True))

    data_sets['adjudicators_positions'].append(compile_data(
        'Chairs', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_CHAIR), 'adjudicator__gender', filters=[
            {'Unknown':  None},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
            {'Male':     Person.GENDER_MALE},
        ], count=True))

    data_sets['adjudicators_positions'].append(compile_data(
        'Panelists', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_PANEL), 'adjudicator__gender', filters=[
            {'Unknown':  None},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
            {'Male':     Person.GENDER_MALE},
        ], count=True))

    data_sets['adjudicators_positions'].append(compile_data(
        'Trainees', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_TRAINEE), 'adjudicator__gender', filters=[
            {'Unknown':  None},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
            {'Male':     Person.GENDER_MALE},
        ], count=True))

    # ==========================================================================
    # Adjudicators Results
    # ==========================================================================

    data_sets['adjudicators_results'].append(compile_data(
        'Average Rating', AdjudicatorFeedback.objects.filter(adjudicator__tournament=t), 'adjudicator__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], average=True, datum=True))

    data_sets['adjudicators_results'].append(compile_data(
        'Median Rating', AdjudicatorFeedback.objects.filter(adjudicator__tournament=t), 'adjudicator__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], median=True, datum=True))

    data_sets['adjudicators_results'].append(compile_data(
        'Upper Quartile Rating', AdjudicatorFeedback.objects.filter(adjudicator__tournament=t), 'adjudicator__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], upperq=True, datum=True))

    data_sets['adjudicators_results'].append(compile_data(
        'Lower Quartile Rating', AdjudicatorFeedback.objects.filter(adjudicator__tournament=t), 'adjudicator__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], lowerq=True, datum=True))

    # overall = AdjudicatorFeedback.objects.filter(adjudicator__tournament=t)
    # overall = [af for af in list(overall) if af.debate_adjudicator and af.debate_adjudicator.type is DebateAdjudicator.TYPE_CHAIR]

    # data_sets['adjudicators_results'].append(package_data_set('Average Chair Rating', [
    #     {'Male':     sum([af.score for af in overall if af.adjudicator.gender is Person.GENDER_MALE]) / len(overall) - overall},
    #     {'Overall':  sum([af.score for af in overall]) / len(overall)},
    #     {'NM':       sum([af.score for af in overall if af.adjudicator.gender is Person.GENDER_FEMALE or Person.GENDER_OTHER]) / len(overall) - overall},
    # ]))

    # ==========================================================================
    # Speakers Results
    # ==========================================================================

    data_sets['speakers_results'].append(compile_data(
        'Average Score', SpeakerScore.objects.filter(speaker__team__tournament=t), 'speaker__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], average=True, datum=True))

    data_sets['speakers_results'].append(compile_data(
        'Median Score', SpeakerScore.objects.filter(speaker__team__tournament=t), 'speaker__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], median=True, datum=True))

    data_sets['speakers_results'].append(compile_data(
        'Upper Quartile Score', SpeakerScore.objects.filter(speaker__team__tournament=t), 'speaker__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], upperq=True, datum=True))

    data_sets['speakers_results'].append(compile_data(
        'Lower Quartile Score', SpeakerScore.objects.filter(speaker__team__tournament=t), 'speaker__gender', filters=[
            {'Male':     Person.GENDER_MALE},
            {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        ], lowerq=True, datum=True))

    return data_sets
