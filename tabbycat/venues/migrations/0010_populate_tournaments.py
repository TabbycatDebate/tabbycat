from itertools import groupby

from django.db import migrations, models


def find_venue_tournament(apps, schema_editor):
    Venue = apps.get_model('venues', 'Venue')
    Debate = apps.get_model('draw', 'Debate')

    venues = []
    venue_qs = Venue.objects.prefetch_related(
        models.Prefetch('debate_set__round', queryset=Debate.objects.order_by('round').all()),
        'venuecategory_set',
    ).filter(tournament__isnull=True)
    for v in venue_qs:
        cats = [c for c in v.venuecategory_set.all()]
        debate_sets = dict(groupby(v.debate_set.all(), key=lambda x: x.round.tournament_id))
        tournaments = set(debate_sets.keys())
        if len(tournaments) == 1:
            v.tournament_id = next(iter(tournaments))
            venues.append(v)
        elif len(tournaments) > 1:
            for i, (tournament_id, debates) in enumerate(debate_sets.items()):
                if i != 0:  # Resetting pk re-creates the object
                    v.pk = None
                    v.save()
                v.tournament_id = tournament_id
                v.debate_set.set(debates)
                v.venuecategory_set.set(cats)
                v.save()
    Venue.objects.bulk_update(venues, ['tournament_id'])


def find_venuecat_tournament(apps, schema_editor):
    VenueCategory = apps.get_model('venues', 'VenueCategory')
    venuecategories = []
    for vc in VenueCategory.objects.prefetch_related('venues').filter(tournament__isnull=True):
        venue_sets = dict(groupby(vc.venues.all(), key=lambda x: x.tournament_id))
        tournaments = set(venue_sets.keys())
        if len(tournaments) == 1:
            vc.tournament_id = next(iter(tournaments))
            venuecategories.append(vc)
        elif len(tournaments) > 1:
            for i, (tournament_id, venues) in enumerate(venue_sets.items()):
                if i != 0:
                    vc.pk = None
                    vc.save()
                vc.tournament_id = tournament_id
                vc.venues.set(venues)
                vc.save()
    VenueCategory.objects.bulk_update(venuecategories, ['tournament_id'])


def find_venue_tournament_via_category(apps, schema_editor):
    Venue = apps.get_model('venues', 'Venue')
    VenueCategory = apps.get_model('venues', 'VenueCategory')
    venues = []
    venue_qs = Venue.objects.prefetch_related(
        models.Prefetch('venuecategory_set', queryset=VenueCategory.objects.filter(tournament__isnull=False)),
    ).filter(tournament__isnull=True)
    for v in venue_qs:
        category_sets = dict(groupby(v.venuecategory_set.all(), key=lambda x: x.tournament_id))
        if len(category_sets) == 1:
            v.tournament_id = next(iter(category_sets.keys()))
            venues.append(v)
        elif len(category_sets) > 1:
            for i, (tournament_id, categories) in enumerate(category_sets.items()):
                if i != 0:
                    v.pk = None
                    v.save()
                v.tournament_id = tournament_id
                v.venuecategory_set.set(categories)


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0009_auto_20210307_1810'),
    ]

    operations = [
        migrations.RunPython(find_venue_tournament, migrations.RunPython.noop),
        migrations.RunPython(find_venuecat_tournament, migrations.RunPython.noop),
        migrations.RunPython(find_venue_tournament_via_category, migrations.RunPython.noop),
    ]
