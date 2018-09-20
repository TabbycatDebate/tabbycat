from django import template

from ..teams import TeamStandingsGenerator

register = template.Library()


@register.filter
def metricformat(value):
    if isinstance(value, float):
        value = "{0:.2f}".format(value).split('.')
        return value[0] + '<small class="text-muted">' + '.' + value[1] + '</small>'
    else:
        return str(value)


@register.filter
def rankingformat(value):
    # Of the format (1, False); where true/false connotes a shared rank
    if value[0] is None:
        return ""
    string = str(value[0])
    if value[1]:
        string += "="
    return string


@register.filter
def teammetricname(key):
    try:
        metric_class = TeamStandingsGenerator.metric_annotator_classes[key]
    except KeyError:
        return ""
    return metric_class.name
