# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.db import migrations

logger = logging.getLogger(__name__)


def convert_availability(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    RoundAvailability = apps.get_model("availability", "RoundAvailability")

    Checkin = apps.get_model("availability", "Checkin")
    Person = apps.get_model("participants", "Person")
    for checkin in Checkin.objects.all():
        # uniqueness wasn't enforced for Checkin, so need to catch non-unique checkins
        _, created = RoundAvailability.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Person),
            object_id=checkin.person_id, round_id=checkin.round_id)
        if not created:
            logger.warning("Skipping duplicate checkin: person ID %s in round ID %s", checkin.person_id, checkin.round_id)

    ActiveVenue = apps.get_model("availability", "ActiveVenue")
    Venue = apps.get_model("venues", "Venue")
    for av in ActiveVenue.objects.all():
        RoundAvailability.objects.create(
            content_type=ContentType.objects.get_for_model(Venue),
            object_id=av.venue_id, round_id=av.round_id)

    ActiveTeam = apps.get_model("availability", "ActiveTeam")
    Team = apps.get_model("participants", "Team")
    for at in ActiveTeam.objects.all():
        RoundAvailability.objects.create(
            content_type=ContentType.objects.get_for_model(Team),
            object_id=at.team_id, round_id=at.round_id)

    ActiveAdjudicator = apps.get_model("availability", "ActiveAdjudicator")
    Adjudicator = apps.get_model("participants", "Adjudicator")
    for aa in ActiveAdjudicator.objects.all():
        RoundAvailability.objects.create(
            content_type=ContentType.objects.get_for_model(Adjudicator),
            object_id=aa.adjudicator_id, round_id=aa.round_id)


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0004_auto_20160905_0034'),
        ('participants', '0019_allow_blank_team_reference'),  # Person, Team, Adjudicator, Institution (select_related by Adjudicator)
        ('venues', '0008_auto_20160621_1129'),  # Venue
        ('tournaments', '0013_remove_tournament_release_all'),  # Round
    ]

    operations = [
        migrations.RunPython(convert_availability),
    ]
