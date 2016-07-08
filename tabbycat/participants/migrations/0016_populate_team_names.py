# -*- coding: utf-8 -*-

# This is a data migration. It was written manually and its purpose is to
# populate the fields added by the migration
# 0015_add_team_short_name_add_team_long_name.

from __future__ import unicode_literals

from django.db import migrations


def _construct_short_name(team):
    institution = team.institution
    name = team.short_reference or team.reference
    if team.use_institution_prefix:
        if institution.code:
            return institution.code + " " + name
        else:
            return institution.abbreviation + " " + name
    else:
        return name

def _construct_long_name(team):
    institution = team.institution
    if team.use_institution_prefix:
        return institution.name + " " + team.reference
    else:
        return team.reference

def populate_team_names(apps, schema_editor):
    Team = apps.get_model("participants", "Team")
    for team in Team.objects.all():
        team.short_name = _construct_short_name(team)
        team.long_name = _construct_long_name(team)
        team.save()


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0015_add_team_short_name_add_team_long_name'),
    ]

    operations = [
        migrations.RunPython(populate_team_names),
    ]
