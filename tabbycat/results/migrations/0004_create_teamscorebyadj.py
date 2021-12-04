import itertools

from django.db import migrations, models
import django.db.models.deletion
import results.models


def populate_teamscorebyadj(apps, schema_editor):
    SpeakerScoreByAdj = apps.get_model("results", "speakerscorebyadj")
    TeamScoreByAdj = apps.get_model("results", "teamscorebyadj")

    ss_query = SpeakerScoreByAdj.objects.all().order_by(
        'ballot_submission_id', 'debate_adjudicator_id', 'debate_team_id'
    ).values()

    # Create nested dicts {ballot: {adj: {team: score, ...}, ...}, ...}
    ss_by_ballot = {}
    for key, group in itertools.groupby(ss_query, lambda ss: ss["ballot_submission_id"]):
        ss_by_adj = {}
        for adj_key, adj_group in itertools.groupby(group, lambda ss: ss["debate_adjudicator_id"]):
            s = {team_key: sum(t["score"] for t in team_group) for team_key, team_group in itertools.groupby(adj_group, lambda ss: ss["debate_team_id"])}
            ss_by_adj[adj_key] = s
        ss_by_ballot[key] = ss_by_adj

    # Calculate win/margin (2-team formats only) & add TSA object
    teamscores = []
    for ballot, adjs_scores in ss_by_ballot.items():
        for adj, teams in adjs_scores.items():
            winner = max(teams.items(), key=(lambda v: v[1]))[0]
            margin = max(teams.values()) - min(teams.values())
            for team, score in teams.items():
                tsa = TeamScoreByAdj(ballot_submission_id=ballot, debate_adjudicator_id=adj, debate_team_id=team, score=score)
                tsa.win = team == winner
                tsa.margin = margin if tsa.win else -margin
                teamscores.append(tsa)
    TeamScoreByAdj.objects.bulk_create(teamscores)


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
        migrations.RunPython(
            populate_teamscorebyadj,
            lambda apps, schema_editor: apps.get_model("results", "teamscorebyadj").objects.all().delete(),
        ),
    ]
