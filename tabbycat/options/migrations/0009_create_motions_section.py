from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0008_auto_20190906_1310'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE options_tournamentpreferencemodel SET section='motions' WHERE name IN ('enable_motions', 'motion_vetoes_enabled')",
            "UPDATE options_tournamentpreferencemodel SET section=CASE WHEN name='enable_motions' THEN 'data_entry' ELSE 'debate_rules' END WHERE name IN ('enable_motions', 'motion_vetoes_enabled')",
        ),
    ]
