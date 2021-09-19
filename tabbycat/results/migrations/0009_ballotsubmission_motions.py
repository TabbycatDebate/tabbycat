from django.db import migrations
from django.db.models import Count, Prefetch


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0008_auto_20201126_0037'),
        ('motions', '0005_motions_mtm'),
        ('options', '0009_create_motions_section'),
    ]

# Complicated query, gets all motions from rounds with only one motion and
# where the tournament has "enable_motions" false/null, and correlates them
# to a debate and then sets the ballotsubmission motion field, if null.
    operations = [
        migrations.RunSQL(
            """
UPDATE results_ballotsubmission bs SET motion_id=rm.motion_id
    FROM draw_debate d
    INNER JOIN tournaments_round r ON d.round_id=r.id
    INNER JOIN tournaments_tournament t ON r.tournament_id=t.id
    LEFT JOIN options_tournamentpreferencemodel p ON p.instance_id=t.id AND p.name = 'enable_motions'
    INNER JOIN (
        SELECT round_id, motion_id FROM motions_roundmotion WHERE round_id IN (
            SELECT round_id FROM motions_roundmotion GROUP BY round_id HAVING COUNT(motion_id)=1)) rm
        ON r.id=rm.round_id
    WHERE d.id=bs.debate_id AND bs.motion_id IS NULL AND (p.raw_value='False' OR p.raw_value IS NULL)""",
            """
UPDATE results_ballotsubmission bs SET motion_id=NULL
    FROM draw_debate d
    INNER JOIN tournaments_round r ON d.round_id=r.id
    INNER JOIN tournaments_tournament t ON r.tournament_id=t.id
    LEFT JOIN options_tournamentpreferencemodel p ON p.instance_id=t.id AND p.name = 'enable_motions'
    INNER JOIN (
        SELECT round_id, motion_id FROM motions_roundmotion WHERE round_id IN (
            SELECT round_id FROM motions_roundmotion GROUP BY round_id HAVING COUNT(motion_id)=1)) rm
        ON r.id=rm.round_id
    WHERE d.id=bs.debate_id AND (p.raw_value='False' OR p.raw_value IS NULL)"""),
    ]
