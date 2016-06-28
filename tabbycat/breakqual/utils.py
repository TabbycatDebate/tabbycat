import json

from .models import BreakCategory


def categories_to_json(t):
    return json.dumps(categories_ordered(t))


def categories_ordered(t):
    categories = BreakCategory.objects.filter(tournament=t).order_by('-is_general', 'name')
    data = [{
        'seq': count + 1,
        'name': r.name,
        'id': r.id
    } for count, r in enumerate(categories)]
    return data
