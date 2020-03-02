from draw.models import Debate
from results.models import BallotSubmission
from tournaments.models import Round, Tournament
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = (
        "Compares ballots between an original tournament and a check tournament "
        "set up to mimic the original tournament. This requires advanced use to "
        "set up, and is not intended for general use. Don't use unless you know "
        "what you're doing.",
    )

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("-c", "--compare", type=str, required=True,
                            help="Tournament to compare to")

    def handle_tournament(self, tournament, **options):

        compare_tournament = Tournament.objects.get(slug=options['compare'])
        debates = Debate.objects.filter(round__tournament=tournament, round__stage=Round.STAGE_PRELIMINARY)

        no_original = 0
        no_check = 0

        for debate in debates:
            if not debate.confirmed_ballot:
                no_original += 1
                continue

            original = debate.confirmed_ballot

            try:
                compare = BallotSubmission.objects.get(
                    debate__round__tournament=compare_tournament,
                    debate__round__seq=debate.round.seq,
                    debate__venue=debate.venue,
                    debate__room_rank=debate.room_rank,
                )
            except BallotSubmission.DoesNotExist:
                no_check += 1
                continue

            # Can't use DebateResult.identical(), because this involves different objects

            if original.motion != compare.motion:
                self.stdout.write("{debate}: original motion={orig}, check motion={check}".format(
                    debate=debate, orig=original.motion.reference, check=compare.motion.reference))

            for ts in original.teamscore_set.all():
                cts = compare.teamscore_set.get(debate_team__side=ts.debate_team.side)
                for field in ['points', 'win', 'margin', 'score', 'votes_given', 'votes_possible']:
                    if getattr(ts, field) != getattr(cts, field):
                        self.stdout.write("{dt}: original {field}={orig}, check {field}={check}".format(
                            dt=ts.debate_team, orig=getattr(ts, field),
                            check=getattr(cts, field), field=field))

            for ss in original.speakerscore_set.all():
                css = compare.speakerscore_set.get(debate_team__side=ss.debate_team.side, position=ss.position)
                for field in ['speaker', 'score', 'ghost']:
                    if getattr(ss, field) != getattr(css, field):
                        message = "{dt}, speaker {pos}: original {field}={orig}, check {field}={check}".format(
                            dt=ss.debate_team, pos=ss.position, orig=getattr(ss, field),
                            check=getattr(css, field), field=field)
                        if field == 'speaker':
                            message += " (original score {})".format(ss.score)
                        self.stdout.write(message)

            for ssba in original.speakerscorebyadj_set.all():
                cssba = compare.speakerscorebyadj_set.get(
                    debate_team__side=ssba.debate_team.side,
                    debate_adjudicator=ssba.debate_adjudicator,
                    position=ssba.position,
                )
                if ssba.score != cssba.score:
                    self.stdout.write("{dt}, speaker {pos}, from {adj}: original score={orig}, check score={check}".format(
                        dt=ssba.debate_team, pos=ssba.position, adj=ssba.debate_adjudicator.adjudicator,
                        orig=ssba.score, check=cssba.score))

        if no_original:
            self.stdout.write("WARNING: original ballots for {:d} debates not found".format(no_original))
        if no_check:
            self.stdout.write("WARNING: check ballots for {:d} debates not found".format(no_check))
