import itertools

from django.db import migrations, models
import django.db.models.deletion
import results.models


class Migration(migrations.Migration):

    dependencies = [
        ('adjallocation', '0008_auto_20181019_2059'),
        ('draw', '0003_remove_debate_ballot_in'),
        ('results', '0003_remove_league_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamScoreByAdj',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('win', models.BooleanField(null=True, verbose_name='win')),
                ('margin', results.models.ScoreField(blank=True, null=True, verbose_name='margin')),
                ('score', results.models.ScoreField(blank=True, null=True, verbose_name='score')),
                ('ballot_submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.BallotSubmission', verbose_name='ballot submission')),
                ('debate_adjudicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adjallocation.DebateAdjudicator', verbose_name='debate adjudicator')),
                ('debate_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='draw.DebateTeam', verbose_name='debate team')),
            ],
            options={
                'verbose_name': 'team score by adjudicator',
                'verbose_name_plural': 'team scores by adjudicator',
            },
        ),
        migrations.AlterUniqueTogether(
            name='teamscorebyadj',
            unique_together={('debate_adjudicator', 'debate_team', 'ballot_submission')},
        ),
        migrations.AlterIndexTogether(
            name='teamscorebyadj',
            index_together={('ballot_submission', 'debate_adjudicator')},
        ),
        migrations.RunSQL(
            "WITH tadj AS (SELECT SUM(score) score, ballot_submission_id, debate_adjudicator_id, debate_team_id FROM results_speakerscorebyadj GROUP BY ballot_submission_id, debate_adjudicator_id, debate_team_id) INSERT INTO results_teamscorebyadj (win, margin, score, ballot_submission_id, debate_adjudicator_id, debate_team_id) SELECT score = max_score, CASE WHEN score = max_score THEN max_score - min_score ELSE min_score - max_score END, t.score, t.ballot_submission_id, t.debate_adjudicator_id, debate_team_id FROM tadj t INNER JOIN (SELECT MAX(score) max_score, MIN(score) min_score, ballot_submission_id, debate_adjudicator_id FROM tadj GROUP BY ballot_submission_id, debate_adjudicator_id) b ON t.ballot_submission_id=b.ballot_submission_id AND t.debate_adjudicator_id=b.debate_adjudicator_id;",
            migrations.RunSQL.noop,
        ),
    ]
