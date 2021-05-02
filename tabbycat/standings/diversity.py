from django.db.models import Aggregate, Avg, Case, CharField, Count, F, Value, When
from django.utils.translation import gettext as _

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
        When(**{'%s__in' % gender_field: (Person.GENDER_FEMALE, Person.GENDER_OTHER), 'then': Value('N')}),
        When(**{gender_field: Person.GENDER_MALE, 'then': Value('M')}),
        default=Value('-'),
        output_field=CharField(),
    )


def _group_data(get_statistic, group_values, group_labels):
    data = []
    for value, label in zip(group_values, group_labels):
        try:
            count = get_statistic(value)
        except KeyError:
            continue
        data.append({'count': count, 'label': label})
    return data


def compile_statistics_by_gender(titles, queryset, statistics, gender_field):
    aggregates = {key: value for key, value in STATISTICS_MAP.items() if key in statistics}
    overall_statistics = queryset.aggregate(**aggregates)
    gender_statistics = queryset.values(gender=_gender_group(gender_field)).annotate(**aggregates)
    gender_statistics = {d['gender']: d for d in gender_statistics}

    results = []
    for title, statistic in zip(titles, statistics):
        result = {'title': title}
        result['datum'] = overall_statistics[statistic]
        result['data'] = _group_data(lambda gender: gender_statistics[gender][statistic], ['N', 'M'], ['NM', 'Male'])
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
        result['data'] = _group_data(lambda gender: gender_means[(group, gender)], ['N', 'M'], ['NM', 'Male'])
        results.append(result)

    return results


def compile_gender_counts(title, queryset, gender_field):
    return compile_grouped_counts(title, queryset, _gender_group(gender_field), ['N', 'M', '-'], ['NM', 'Male', 'Unknown'])


def compile_grouped_counts(title, queryset, group_field, group_values, group_labels):
    counts = queryset.values(group=group_field).annotate(count=Count(Value(1)))  # Count counts records, value doesn't matter
    counts = {d['group']: d['count'] for d in counts}
    result = {'title': title}
    result['data'] = _group_data(lambda group: counts[group], group_values, group_labels)
    return result


def compile_grouped_gender_counts(titles, queryset, gender_field, group_field, group_values):
    counts = queryset.values(group_field, gender_group=_gender_group(gender_field)).annotate(count=Count(Value(1)))
    counts = {(d[group_field], d['gender_group']): d['count'] for d in counts}
    results = []
    for title, group in zip(titles, group_values):
        result = {'title': title}
        result['data'] = _group_data(lambda gender: counts[(group, gender)], ['N', 'M', '-'], ['NM', 'Male', 'Unknown'])
        results.append(result)
    return results


def get_diversity_data_sets(t, for_public):

    all_regions = regions_ordered(t)

    region_values = [r['id'] for r in all_regions]
    region_labels = [r['seq'] for r in all_regions]

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
        'regions': all_regions,  # For CSS
    }

    # ==========================================================================
    # Speakers Demographics
    # ==========================================================================

    speakers = Speaker.objects.filter(team__tournament=t)

    if Speaker.objects.filter(team__tournament=t).count() > 0:
        data_sets['speakers_gender'].append(compile_gender_counts(_("All"), speakers, 'gender'))

    if t.pref('public_breaking_teams') is True or for_public is False:
        if Speaker.objects.filter(team__tournament=t).filter(team__breakingteam__isnull=False).count() > 0:
            data_sets['speakers_gender'].append(compile_gender_counts(_("Breaking"),
                    speakers.filter(team__breakingteam__isnull=False), 'gender'))

    for sc in SpeakerCategory.objects.filter(tournament=t).order_by('seq'):
        if Speaker.objects.filter(categories=sc).count() > 0:
            data_sets['speakers_categories'].append(compile_gender_counts(sc.name,
                    speakers.filter(categories=sc), 'gender'))
            data_sets['speakers_categories'].append(compile_gender_counts(_("Not %(category)s") % {'category': sc.name},
                    speakers.exclude(categories=sc), 'gender'))

    if Team.objects.exclude(institution__region__isnull=True).exists():
        data_sets['speakers_region'].append(compile_grouped_counts(_("All Speakers"), speakers,
                F('team__institution__region__id'), region_values, region_labels))

        if t.pref('public_breaking_teams') is True or for_public is False:
            data_sets['speakers_region'].append(compile_grouped_counts(_("Breaking"),
                    speakers.filter(team__breakingteam__isnull=False),
                    F('team__institution__region__id'), region_values, region_labels))

    # ==========================================================================
    # Adjudicators Demographics
    # ==========================================================================

    adjudicators = t.adjudicator_set.all()

    if adjudicators.count() > 0:
        data_sets['adjudicators_gender'].append(compile_gender_counts(_("All"), adjudicators, 'gender'))

    if Adjudicator.objects.filter(tournament=t).filter(independent=True).exists():
        data_sets['adjudicators_gender'].append(compile_gender_counts(_("IAs"),
            adjudicators.filter(independent=True), 'gender'))

    if (t.pref('public_breaking_adjs') is True or for_public is False) and Adjudicator.objects.filter(breaking=True).exists():
        data_sets['adjudicators_gender'].append(compile_gender_counts(_("Breaking"),
            adjudicators.filter(breaking=True), 'gender'))

    debateadjs = DebateAdjudicator.objects.filter(adjudicator__tournament=t)
    titles = [_("Chairs"), _("Panellists"), _("Trainees")]
    adjtypes = [
        DebateAdjudicator.TYPE_CHAIR,
        DebateAdjudicator.TYPE_PANEL,
        DebateAdjudicator.TYPE_TRAINEE,
    ]
    data_sets['adjudicators_position'] = compile_grouped_gender_counts(titles, debateadjs,
            'adjudicator__gender', 'type', adjtypes)

    if Adjudicator.objects.exclude(institution__region__isnull=True).exists():
        data_sets['adjudicators_region'].append(compile_grouped_counts(_("All"), adjudicators,
                F('institution__region__id'), region_values, region_labels))

        if t.pref('public_breaking_adjs') is True or for_public is False:
            data_sets['adjudicators_region'].append(compile_grouped_counts(_("Breaking"), adjudicators.filter(breaking=True),
                    F('institution__region__id'), region_values, region_labels))

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
                _("Average Rating From Teams"),
                _("Average Rating From Chairs"),
                _("Average Rating From Panellists"),
                _("Average Rating From Trainees"),
            ]
            group_values = [
                None,
                DebateAdjudicator.TYPE_CHAIR,
                DebateAdjudicator.TYPE_PANEL,
                DebateAdjudicator.TYPE_TRAINEE,
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
            data_sets['speakers_results'] = compile_statistics_by_gender(titles,
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
