from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0009_create_motions_section'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE options_tournamentpreferencemodel SET raw_value=CASE WHEN raw_value='two' THEN '2' WHEN raw_value='bp' THEN '4' ELSE '2' END WHERE name='teams_in_debate'",
            "UPDATE options_tournamentpreferencemodel SET raw_value=CASE WHEN raw_value='2' THEN 'two' WHEN raw_value='4' THEN 'bp' ELSE 'two' END WHERE name='teams_in_debate'",
        ),
    ]
