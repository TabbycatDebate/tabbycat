from standings.teams import TeamStandingsGenerator


class BreakGeneratorError(RuntimeError):
    pass


class BaseBreakGenerator:
    """Base class for break generators.

    A break generator is responsible for populating the database with the
    list of breaking teams.

    The main method is `generate()`, which runs four steps:

    1. `retrieve_standings()`, which sets `self.standings` to a TeamStandings
       object. This function uses the metrics set in the tournament preferences,
       and the rankings

    2. `exclude_ineligible_teams()`, which sets `self.excluded_teams` to a dict
       mapping TeamStandingInfo objects to BreakingTeam.REMARK_* constants.

    3. `compute_break()`, which sets `self.breaking_teams` to a list of
       TeamStandingInfo objects, corresponding to the breaking teams (in order).
       Subclasses must implement this method. The implementation should include
       all teams that are tied in the last breaking place (e.g. if 16 teams
       break and two teams are tied 16th equal, the list should have 17 teams).

    4. `populate_database()`, which writes the computed break and excluded teams
       to the database.
    """

    rule = None
    required_metrics = ()
    rankings = ()

    def __init__(self, category):
        """`category` is a BreakCategory instance."""
        self.category = category

    def generate(self):
        self.retrieve_standings()
        self.exclude_ineligible_teams()
        self.compute_break()
        self.populate_database()

    def check_required_metrics(self, metrics):
        """Checks that all metrics required for this break rule are included,
        and raises a BreakGeneratorError if they're not."""

        missing_metrics = [metric for metric in self.required_metrics if metric not in metrics]

        if missing_metrics:

            def _metric_name(metric):
                try:
                    annotator_class = TeamStandingsGenerator.metric_annotator_classes[metric]
                except KeyError:
                    return "<unknown metric>"
                if hasattr(annotator_class, 'choice_name'):
                    return annotator_class.choice_name
                else:
                    return annotator_class.name

            raise BreakGeneratorError("The break qualification rule {rule} "
                "requires the following metric(s) to be in the team standings "
                "precedence in order to work: {required}; and the following "
                "are missing: {missing}.".format(
                    rule=self.category.get_rule_display(),
                    required=", ".join(_metric_name(metric) for metric in self.required_metrics),
                    missing=", ".join(_metric_name(metric) for metric in missing_metrics),
                ))

    def retrieve_standings(self):
        """Retrieves standings and places them in `self.standings`."""

        if self.category.is_general:
            teams = self.category.tournament.team_set.all()
        else:
            teams = self.category.team_set.all()

        metrics = self.category.tournament.pref('team_standings_precedence')
        self.check_required_metrics(metrics)

        generator = TeamStandingsGenerator(metrics, self.rankings)
        generated = generator.generate(teams)
        self.standings = list(generated)

    def exclude_ineligible_teams(self):
        """Excludes teams that are ineligible for this break by adding them to
        `self.excluded_teams`.

        Most subclasses shouldn't need to modify this method. Specifically, it
        excludes the following:
         - teams not eligible for this break category (if it is a general category)
         - teams that broke in a higher-priority break
         - teams that have an existing remark

        The purpose of this method is to catch teams that shouldn't even be
        considered for the break. It's not intended to cover cases where teams
        are ruled out due to other teams in the break, for example, the AIDA
        institution cap. Such cases should be accounted for directly in the
        `compute_break()` method.
        """

    def compute_break(self):
        """Subclasses must implement this method. It must populate two
        attributes: `self.breaking_teams` and `self.excluded_teams`.
        `self.breaking_teams` must be a list of TeamStandingInfo objects,
        each one being ."""

    def populate_database(self):
        """Populates the database."""


class StandardBreakGenerator(BaseBreakGenerator):
    pass
