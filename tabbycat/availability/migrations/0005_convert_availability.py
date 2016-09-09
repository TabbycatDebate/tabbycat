# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.db import IntegrityError, migrations

logger = logging.getLogger(__name__)


def convert_availability(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    RoundAvailability = apps.get_model("availability", "RoundAvailability")

    Checkin = apps.get_model("availability", "Checkin")
    person_content_type = ContentType.objects.get_for_model(apps.get_model("participants", "Person"))
    for checkin in Checkin.objects.all():
        # uniqueness wasn't enforced for Checkin, so need to catch non-unique checkins
        _, created = RoundAvailability.objects.get_or_create(content_type=person_content_type,
                    object_id=checkin.person_id, round=checkin.round)
        if not created:
            logger.warning("Skipping duplicate checkin: %s in %s", checkin.person.name, checkin.round.name)

    ActiveVenue = apps.get_model("availability", "ActiveVenue")
    venue_content_type = ContentType.objects.get_for_model(apps.get_model("venues", "Venue"))
    for av in ActiveVenue.objects.all():
        RoundAvailability.objects.create(content_type=venue_content_type,
                object_id=av.venue_id, round=av.round)

    ActiveTeam = apps.get_model("availability", "ActiveTeam")
    team_content_type = ContentType.objects.get_for_model(apps.get_model("participants", "Team"))
    for at in ActiveTeam.objects.all():
        RoundAvailability.objects.create(content_type=team_content_type,
                object_id=at.team_id, round=at.round)

    ActiveAdjudicator = apps.get_model("availability", "ActiveAdjudicator")
    adjudicator_content_type = ContentType.objects.get_for_model(apps.get_model("participants", "Adjudicator"))
    for aa in ActiveAdjudicator.objects.all():
        RoundAvailability.objects.create(content_type=adjudicator_content_type,
                object_id=aa.adjudicator_id, round=aa.round)


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0004_auto_20160905_0034'),
        ('participants', '0001_initial'),
        ('venues', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_availability),
    ]
