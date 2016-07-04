from .models import Region


def regions_ordered(t):
    '''Need to redo the region IDs so the CSS classes will be consistent. This
    assumes there aren't huge amounts of regions, or dramatically different
    regions between tournaments (which holds for big tournaments uses)'''

    regions = Region.objects.all().order_by('name')
    data = [{
        'seq': count + 1,
        'name': r.name,
        'id': r.id
    } for count, r in enumerate(regions)]
    return data
