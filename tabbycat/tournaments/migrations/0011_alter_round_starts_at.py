# Generated by Django 4.2.5 on 2023-11-18 16:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tournaments", "0010_alter_round_draw_type"),
        ('results', '0010_merge_20210919_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name="round",
            name="starts_at_",
            field=models.DateTimeField(blank=True, null=True, verbose_name="starts at"),
        ),
        migrations.RunSQL(
            "WITH first_ballot AS (SELECT DISTINCT ON (round_id) d.round_id, bs.timestamp FROM results_ballotsubmission bs INNER JOIN draw_debate d ON d.id=bs.debate_id ORDER BY round_id, timestamp) UPDATE tournaments_round r SET starts_at_=fb.timestamp::date + r.starts_at AT TIME ZONE '" + settings.TIME_ZONE + "' FROM first_ballot fb WHERE r.id=fb.round_id;",
            migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name="round",
            name="starts_at",
        ),
        migrations.RenameField(
            model_name="round",
            old_name="starts_at_",
            new_name="starts_at",
        ),
    ]
