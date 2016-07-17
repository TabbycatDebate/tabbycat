from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Checks for feedback with more than one version."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--num", "-n", type=int,
            help="Show feedback with at least this many versions", default=2)

    def handle_tournament(self, tournament, **options):

        for adj in tournament.adjudicator_set.all():
            seen = list()
            for feedback in adj.adjudicatorfeedback_set.all():
                if feedback.source in seen:
                    continue
                seen.append(feedback.source)
                others = adj.adjudicatorfeedback_set.filter(
                    source_adjudicator=feedback.source_adjudicator,
                    source_team=feedback.source_team).order_by('version')
                num = others.count()
                if num >= options["num"]:
                    self.stdout.write(self.style.MIGRATE_HEADING(
                        " *** Adjudicator: {0}, from: {1}, {2:d} versions".format(adj, feedback.source, num)))
                    for other in others:
                        self.stdout.write("   {id:>3} {submitter:<12} {round:<4} {c} {version} {score:.1f}".format(
                            score=other.score, version=other.version, round=other.round.abbreviation, submitter=other.submitter.username,
                            id=other.id, c="c" if other.confirmed else "-"))
