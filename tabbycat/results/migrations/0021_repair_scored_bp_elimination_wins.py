from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0020_ballotsubmission_self_split'),
    ]

    operations = [
        migrations.RunSQL(
            """
            WITH affected_ballots AS (
                SELECT ts.ballot_submission_id, r.id AS round_id
                FROM results_teamscore ts
                JOIN results_ballotsubmission bs ON bs.id = ts.ballot_submission_id
                JOIN draw_debateteam dt ON dt.id = ts.debate_team_id
                JOIN draw_debate d ON d.id = dt.debate_id AND d.id = bs.debate_id
                JOIN tournaments_round r ON r.id = d.round_id
                WHERE r.stage = 'E' AND NOT bs.forfeit
                GROUP BY ts.ballot_submission_id, r.id
                HAVING COUNT(*) = 4 AND COUNT(DISTINCT ts.points) = 4
                    AND MIN(ts.points) = 0 AND MAX(ts.points) = 3
                    AND COUNT(ts.score) = 4 AND BOOL_AND(ts.win IS FALSE)
            ), advancing_thresholds AS (
                SELECT ab.ballot_submission_id,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM tournaments_round later
                        WHERE later.tournament_id = r.tournament_id AND later.seq > r.seq
                            AND (later.stage = 'P'
                                OR later.break_category_id IS NOT DISTINCT FROM r.break_category_id)
                    ) THEN 2 ELSE 3 END AS points_to_advance
                FROM affected_ballots ab
                JOIN tournaments_round r ON r.id = ab.round_id
            )
            UPDATE results_teamscore ts
            SET win = (ts.points >= a.points_to_advance)
            FROM advancing_thresholds a
            WHERE ts.ballot_submission_id = a.ballot_submission_id
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
