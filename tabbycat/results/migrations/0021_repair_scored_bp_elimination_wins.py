from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0020_ballotsubmission_self_split'),
    ]

    operations = [
        migrations.RunSQL(
            """
            WITH affected_ballots AS (
                SELECT ts.ballot_submission_id,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM tournaments_round later
                        WHERE later.tournament_id = r.tournament_id AND later.seq > r.seq
                            AND (later.stage = 'P'
                                OR later.break_category_id IS NOT DISTINCT FROM r.break_category_id)
                    ) THEN 2 ELSE 3 END AS points_to_advance
                FROM results_teamscore ts
                JOIN results_ballotsubmission bs ON bs.id = ts.ballot_submission_id
                JOIN draw_debate d ON d.id = bs.debate_id
                JOIN tournaments_round r ON r.id = d.round_id
                WHERE r.stage = 'E' AND NOT bs.forfeit
                GROUP BY ts.ballot_submission_id, r.id
                HAVING COUNT(ts.ballot_submission_id) = 4
                    AND BOOL_AND(ts.score IS NOT NULL AND ts.points IS NOT NULL AND ts.win IS FALSE)
            )
            UPDATE results_teamscore ts
            SET win = TRUE
            FROM affected_ballots a
            WHERE ts.ballot_submission_id = a.ballot_submission_id
                AND ts.points >= a.points_to_advance
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
