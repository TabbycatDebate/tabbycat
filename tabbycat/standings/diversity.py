from django.db.models import Aggregate, Avg, Case, CharField, Q, Value, When
from django.utils.translation import ugettext as _

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from participants.models import Adjudicator, Person, Speaker, SpeakerCategory, Team
from participants.utils import regions_ordered
from results.models import SpeakerScore
from tournaments.models import Round


class Percentile(Aggregate):
    function = 'PERCENTILE_CONT'
    name = "percentile"
    template = "%(function)s(%(percentiles)s) WITHIN GROUP (ORDER BY %(expressions)s)"

    # Make percentiles a positional argument
    def __init__(self, expression, percentiles, **extra):
        return super().__init__(expression, percentiles=percentiles, **extra)


STATISTICS_MAP = {
    'mean': Avg('score'),
    'upperq': Percentile('score', 0.75),
    'median': Percentile('score', 0.5),
    'lowerq': Percentile('score', 0.25),
}


def _gender_group(gender_field):
    return Case(
        When(**{'%s__in' % gender_field: ['F', 'O'], 'then': Value('N')}),
        default=gender_field,
        output_field=CharField(),
    )


def compile_statistics_by_gender(titles, queryset, statistics, gender_field):
    aggregates = {key: value for key, value in STATISTICS_MAP.items() if key in statistics}
    overall_statistics = queryset.aggregate(**aggregates)
    gender_statistics = queryset.values(gender=_gender_group(gender_field)).annotate(**aggregates)
    gender_statistics = {d['gender']: d for d in gender_statistics}

    results = []
    for title, statistic in zip(titles, statistics):
        result = {'title': title}
        result['datum'] = overall_statistics[statistic]
        result['data'] = [
            {'count': gender_statistics['N'][statistic], 'label': 'NM'},
            {'count': gender_statistics['M'][statistic], 'label': 'Male'},
        ]
        results.append(result)

    return results

def compile_grouped_means_by_gender(titles, queryset, gender_field, group_field, group_values):
    overall_means = queryset.values(group_field).annotate(Avg('score'))
    overall_means = {d[group_field]: d['score__avg'] for d in overall_means}
    gender_means = queryset.values(group_field, gender=_gender_group(gender_field)).annotate(Avg('score'))
    gender_means = {(d[group_field], d['gender']): d['score__avg'] for d in gender_means}

    results = []
    for title, group in zip(titles, group_values):
        result = {'title': title}
        try:
            result['datum'] = overall_means[group]
        except KeyError:
            continue  # no data available, omit from table
        result['data'] = [
            {'count': gender_means[(group, 'N')], 'label': 'NM'},
            {'count': gender_means[(group, 'M')], 'label': 'Male'},
        ]
        results.append(result)

    return results


def compile_data(title, queryset, filter_source, filters, **kwargs):
    """ Filter the queryset given filters and return a dictionary of results """

    data_set = []
    for item in filters:
        [(key, value)] = item.items()  # Get the key/value pairs

        # Use keywords to filter data sets; using Q for OR conditions
        if isinstance(value, list):
            filtered = queryset.filter(Q(**{filter_source: value[0]}) | Q(**{filter_source: value[1]}))
        else:
            filtered = queryset.filter(**{filter_source: value})

        # Return a structure ready to fit the Vue template
        data_set.append({
            'label': key,
            'count': filtered.count(),
        })

    return {'title': title, 'data': data_set}


def get_diversity_data_sets(t, for_public):

    all_regions = regions_ordered(t)
    region_filters = [{r['seq']:r['name']} for r in all_regions]

    data_sets = {
        'speakers_gender': [],
        'speakers_region': [],
        'speakers_results': [],
        'speakers_categories': [],
        'detailed_speakers_results': [],
        'adjudicators_gender': [],
        'adjudicators_position': [],
        'adjudicators_region': [],
        'adjudicators_results': [],
        'detailed_adjudicators_results': [],
        'regions': all_regions  # For CSS
    }

    # ==========================================================================
    # Speakers Demographics
    # ==========================================================================

    gender_filters = [
        {'NM':       [Person.GENDER_FEMALE, Person.GENDER_OTHER]},
        {'Male':     Person.GENDER_MALE},
        {'Unknown':  None},
    ]

    if Speaker.objects.filter(team__tournament=t).count() > 0:
        data_sets['speakers_gender'].append(compile_data(
            'All', Speaker.objects.filter(team__tournament=t),
            'gender', filters=gender_filters, count=True))

    if t.pref('public_breaking_teams') is True or for_public is False:
        if Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False).count() > 0:
            data_sets['speakers_gender'].append(compile_data(
                'Breaking', Speaker.objects.filter(team__tournament=t, team__breakingteam__isnull=False),
                'gender', filters=gender_filters, count=True))

    for sc in SpeakerCategory.objects.filter(tournament=t).order_by('seq'):
        if Speaker.objects.filter(categories=sc).count() > 0:
            data_sets['speakers_categories'].append(compile_data(
                sc.name, Speaker.objects.filter(team__tournament=t, categories=sc),
                'gender', filters=gender_filters, count=True))
            data_sets['speakers_categories'].append(compile_data(
                'Not ' + sc.name, Speaker.objects.filter(team__tournament=t).exclude(categories=sc),
                'gender', filters=gender_filters, count=True))

    if Team.objects.exclude(institution__region__isnull=True).count() > 0:
        data_sets['speakers_region'].append(compile_data(
            'All', Speaker.objects.filter(
                team__tournament=t), 'team__institution__region__name', filters=region_filters, count=True))
        if t.pref('public_breaking_teams') is True or for_public is False:
            data_sets['speakers_region'].append(compile_data(
                'Breaking', Speaker.objects.filter(team__tournament=t, team__breakingteam__isnull=False), 'team__institution__region__name',
                filters=region_filters, count=True))

    # ==========================================================================
    # Adjudicators Demographics
    # ==========================================================================

    if Adjudicator.objects.filter(tournament=t).count() > 0:
        data_sets['adjudicators_gender'].append(compile_data(
            'All', Adjudicator.objects.filter(tournament=t),
            'gender', filters=gender_filters, count=True))

    if Adjudicator.objects.filter(tournament=t).filter(independent=True).count() > 0:
        data_sets['adjudicators_gender'].append(compile_data(
            'Indies', Adjudicator.objects.filter(tournament=t, independent=True), 'gender',
            filters=gender_filters, count=True))

    if t.pref('public_breaking_adjs') is True or for_public is False:
        if Adjudicator.objects.filter(breaking=True).count() > 0:
            data_sets['adjudicators_gender'].append(compile_data(
                'Breaking', Adjudicator.objects.filter(tournament=t, breaking=True), 'gender',
                filters=gender_filters, count=True))

    if DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_CHAIR).count() > 0:
        data_sets['adjudicators_position'].append(compile_data(
            'Chairs', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_CHAIR), 'adjudicator__gender',
            filters=gender_filters, count=True))

    if DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_PANEL).count() > 0:
        data_sets['adjudicators_position'].append(compile_data(
            'Panellists', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_PANEL), 'adjudicator__gender',
            filters=gender_filters, count=True))

    if DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_TRAINEE).count() > 0:
        data_sets['adjudicators_position'].append(compile_data(
            'Trainees', DebateAdjudicator.objects.filter(adjudicator__tournament=t, type=DebateAdjudicator.TYPE_TRAINEE), 'adjudicator__gender',
            filters=gender_filters, count=True))

    if DebateAdjudicator.objects.exclude(adjudicator__institution__region__isnull=True).count() > 0:
        data_sets['adjudicators_region'].append(compile_data(
            'All', Adjudicator.objects.filter(tournament=t), 'institution__region__name',
            filters=region_filters, count=True))
        if t.pref('public_breaking_adjs') is True or for_public is False:
            data_sets['adjudicators_region'].append(compile_data(
                'Breaking', Adjudicator.objects.filter(tournament=t, breaking=True), 'institution__region__name',
                filters=region_filters, count=True))

    # ==========================================================================
    # Adjudicators Results
    # ==========================================================================

    # Don't show data if genders have not been set
    data_sets['gendered_adjudicators'] = Adjudicator.objects.filter(gender="M").count() + Adjudicator.objects.filter(gender="F").count()
    if data_sets['gendered_adjudicators'] > 0:

        adjfeedbacks = AdjudicatorFeedback.objects.filter(adjudicator__tournament=t, confirmed=True)

        data_sets['feedbacks_count'] = adjfeedbacks.count()

        if data_sets['feedbacks_count'] > 0:

            titles = [
                _("Average Rating"),
                _("Median Rating"),
                _("Upper Quartile Rating"),
                _("Lower Quartile Rating"),
            ]
            statistics = ['mean', 'median', 'upperq', 'lowerq']
            data_sets['adjudicators_results'] = compile_statistics_by_gender(titles, adjfeedbacks, statistics, 'adjudicator__gender')

            titles = [
                _("Average Rating Given by Teams"),
                _("Average Rating Given by Chairs"),
                _("Average Rating Given by Panellists"),
                _("Average Rating Given by Trainees"),
            ]
            group_values = [
                None,
                DebateAdjudicator.TYPE_CHAIR,
                DebateAdjudicator.TYPE_PANEL,
                DebateAdjudicator.TYPE_TRAINEE
            ]
            data_sets['detailed_adjudicators_results'] = compile_grouped_means_by_gender(
                    titles, adjfeedbacks, 'adjudicator__gender', 'source_adjudicator__type', group_values)

    # ==========================================================================
    # Speakers Results
    # ==========================================================================

    # Don't show data if genders have not been set
    data_sets['gendered_speakers'] = Speaker.objects.filter(gender="M").count() + Speaker.objects.filter(gender="F").count()
    if data_sets['gendered_speakers'] > 0:

        speakerscores = SpeakerScore.objects.filter(speaker__team__tournament=t, ballot_submission__confirmed=True)

        data_sets['speaks_count'] = speakerscores.count()
        if data_sets['speaks_count'] > 0:

            titles = [
                _("Average Score"),
                _("Median Score"),
                _("Upper Quartile Score"),
                _("Lower Quartile Score"),
            ]
            statistics = ['mean', 'median', 'upperq', 'lowerq']
            data_sets['speaker_results'] = compile_statistics_by_gender(titles,
                    speakerscores.exclude(position=t.reply_position), statistics, 'speaker__gender')

            titles = [
                _("Reply Speaker Average") if pos == t.reply_position else
                _("Speaker %(num)d Average") % {'num': pos}
                for pos in t.positions
            ]
            data_sets['detailed_speakers_results'] = compile_grouped_means_by_gender(
                    titles, speakerscores, 'speaker__gender', 'position', t.positions)

            if speakerscores.filter(debate_team__debate__round__stage=Round.STAGE_ELIMINATION).exists():
                data_sets['detailed_speakers_results'].extend(compile_statistics_by_gender(
                    [_("Average Finals Score")],
                    speakerscores.filter(debate_team__debate__round__stage=Round.STAGE_ELIMINATION).exclude(position=t.reply_position),
                    ['mean'], 'speaker__gender'))

    return data_sets
