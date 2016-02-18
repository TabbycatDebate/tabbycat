from django.core.management.base import BaseCommand, CommandError
import debate.models as m

class Command(BaseCommand):
    help = 'Copy adjudicator allocations back to respective debates'

    def add_arguments(self, parser):
        parser.add_argument('tournament', help="Merged tournament (no need to specify originals)")
        parser.add_argument('round', help="Round seq number")

    def handle(self, *args, **options):

        seq = options['round']

        # Get source tournament and round
        tournament = m.Tournament.objects.get(slug=options['tournament'])
        source_round = m.Round.objects.get(tournament=tournament, seq=seq)

        for source_debate in source_round.debate_set.all():

            target_debates = [d for d in m.Debate.objects.exclude(round__tournament=tournament).filter(
                    bracket=source_debate.bracket, room_rank=source_debate.room_rank) if
                    d.aff_team == source_debate.aff_team and d.neg_team == source_debate.neg_team]
            if len(target_debates) > 1:
                raise CommandError("Found more than one target debate for " + str(source_debate))
            target_debate = target_debates[0]

            self.stdout.write("Copying " + str(source_debate) + " to " + str(target_debate))

            for source_debateadj in source_debate.debateadjudicator_set.all():
                self.stdout.write(" - " + str(source_debateadj))
                source_debateadj.pk = None
                source_debateadj.debate = target_debate
                source_debateadj.save()

