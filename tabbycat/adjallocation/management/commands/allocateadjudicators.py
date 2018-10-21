from django.core.management.base import CommandError

from adjallocation.allocators import registry
from tournaments.models import Round
from utils.management.base import RoundCommand


class Command(RoundCommand):

    help = "Runs the auto-allocator to assign adjudicators to debates"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("-a", "--allocator", choices=registry.keys(), default="hungarian-voting",
            help="Which allocator to use (default: hungarian-voting)")
        parser.add_argument("-p", "--preformed", action="store_true",
            help="Allocate to preformed panels instead")
        parser.add_argument("-f", "--force", action="store_true",
            help="Run even if draw status is not confirmed")
        parser.add_argument("-n", "--dry-run", action="store_true",
            help="Don't write allocation to database, but print out final allocation instead")

    def handle_round(self, round, **options):
        if round.draw_status != Round.STATUS_CONFIRMED and not options["force"]:
            raise CommandError("Draw status isn't confirmed (it's {}), use "
                "--force to run anyway".format(round.get_draw_status_display().lower()))

        if options["preformed"]:
            debates = round.preformedpanel_set.all()
        else:
            debates = round.debate_set.all()

        adjs = round.active_adjudicators.all()
        allocator_class = registry[options["allocator"]]
        allocator = allocator_class(debates, adjs, round)

        allocations = allocator.allocate()

        if not options["dry_run"]:
            for alloc in allocations:
                alloc.save()

        else:
            print("Dry run requested, not saving to database.")
            print("Allocations would be as follows:")
            feedback_weight = round.feedback_weight

            for alloc in allocations:
                print("In {}".format(alloc.container))
                for adj, pos in alloc.with_positions():
                    print("   - {adj.name} ({pos}, {score})".format(
                        adj=adj, pos=pos,
                        score=adj.weighted_score(feedback_weight))
                    )
