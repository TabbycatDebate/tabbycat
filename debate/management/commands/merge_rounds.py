from django.core.management.base import BaseCommand, CommandError
import debate.models as m

class Command(BaseCommand):
    help = 'Merge two tournaments together'

    def add_arguments(self, parser):
        parser.add_argument('tournament', nargs=2, help="Tournament slugs")
        parser.add_argument('round', help="Round seq number (must be same for both tournaments)")
        parser.add_argument('target', help="Tournament to which debates will be copied")

    def handle(self, *args, **options):

        seq = options['round']

        # Get target tournament
        tournament = m.Tournament.objects.get(slug=options['target'])

        # Create target round
        if m.Round.objects.filter(tournament=tournament, seq=seq).exists():
            response = raw_input("Warning: Round {} in tournament {} already exists. Delete? ".format(seq, tournament.slug))
            if response != "yes":
                raise CommandError("Cancelled by user.")
            m.Round.objects.filter(tournament=tournament, seq=seq).delete()

        target_round = m.Round(tournament=tournament, seq=seq, name=str(seq), abbreviation=str(seq),
                draw_type=m.Round.DRAW_POWERPAIRED, stage=m.Round.STAGE_PRELIMINARY,
                draw_status=m.Round.STATUS_CONFIRMED)
        target_round.save()
        tournament.current_round = target_round
        tournament.save()

        # Get source rounds
        source_rounds = [m.Round.objects.get(tournament__slug=slug, seq=seq) for slug in options['tournament']]

        # Copy debates
        for source_round in source_rounds:
            self.stdout.write("\n == " + str(source_round) + " == ")

            for debate in source_round.debate_set.all():

                # Make copy of debate teams first, so we can still iterate
                # through them after saving debate
                debate_teams = debate.debateteam_set.all()

                # Debate
                self.stdout.write("Copying " + str(debate))
                debate.pk = None
                debate.round = target_round
                debate.save()

                # DebateTeams
                for debateteam in debate_teams:
                    self.stdout.write("  - " + str(debateteam))
                    debateteam.pk = None
                    debateteam.debate = debate
                    debateteam.save()
