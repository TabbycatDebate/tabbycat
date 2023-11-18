from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0003_split_up_ballots_per_debate'),
    ]

    operations = [
        migrations.RunSQL(
            "INSERT INTO options_tournamentpreferencemodel (section, name, raw_value, instance_id) SELECT 'public_features', 'tournament_staff', array_to_string(array_agg('<strong>' || n.label || ':</strong> ' || o.raw_value ORDER BY n.seq), '<br />') new_val, instance_id FROM options_tournamentpreferencemodel o INNER JOIN (VALUES (1, 'tab_credit', 'Tabulation'), (2, 'org_credit', 'Organisation'), (3, 'adj_credit', 'Adjudication')) n(seq, name, label) ON o.name=n.name WHERE section='public_features' GROUP BY instance_id ON CONFLICT (section, name, instance_id) DO UPDATE SET raw_value=CASE WHEN options_tournamentpreferencemodel.raw_value='' THEN EXCLUDED.raw_value ELSE options_tournamentpreferencemodel.raw_value END;",
            migrations.RunSQL.noop,
            elidable=True,
        ),
        migrations.RunSQL(
            "DELETE FROM options_tournamentpreferencemodel WHERE section='public_features' AND name IN ('tab_credit', 'org_credit', 'adj_credit');",
            migrations.RunSQL.noop,
            elidable=True,
        ),
    ]
