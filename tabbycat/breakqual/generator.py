import logging
from itertools import groupby

from breakqual.models import BreakingTeam
from standings.teams import TeamStandingsGenerator

logger = logging.getLogger(__name__)


class BreakGeneratorError(RuntimeError):
    pass


class BaseBreakGenerator:
    """Base class for break generators.

    A break generator is responsible for populating the database with the
    list of breaking teams.

    The main method is `generate()`, which runs five steps:

    1. `set_team_queryset()`, which sets `self.team_queryset` to a QuerySet that
       queries all teams relevant to this break category. In the default
       implementation, this is all teams in the tournament if the break category
       is a general break category, and all teams eligible for the break
       category if it is not a general break category.

    2. `retrieve_standings()`, which sets `self.standings` to a TeamStandings
       object. This function uses the metrics set in the tournament preferences,
       and the rankings specified in the `rankings` class attribute.

    3. `filter_eligible_teams()`, which sets `self.excluded_teams` to a dict
       mapping TeamStandingInfo objects to BreakingTeam.REMARK_* constants, and
       sets `self.eligible_teams` to a list of TeamStandingInfo objects for
       eligible teams, in the same order as they were found in `self.standings`.

    4. `compute_break()`, which sets `self.breaking_teams` to a list of
       TeamStandingInfo objects, corresponding to the breaking teams (in order).
       Subclasses must implement this method.

    5. `populate_database()`, which writes the computed break and excluded teams
       to the database.
    """

    name = None  # must be set by subclasses
    key = None  # must be set by subclasses
    required_metrics = ()
    rankings = ()

    def __init__(self, category):
        """`category` is a BreakCategory instance."""
        self.category = category
        self.break_size = category.break_size

    def generate(self):
        self.set_team_queryset()
        self.retrieve_standings()
        self.filter_eligible_teams()
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

    def set_team_queryset(self):
        """Sets `self.team_queryset` to the queryset of all teams relevant to
        this break category."""

        if self.category.is_general:
            self.team_queryset = self.category.tournament.team_set.all()
        else:
            self.team_queryset = self.category.team_set.all()

    def retrieve_standings(self):
        """Retrieves standings and places them in `self.standings`."""

        metrics = self.category.tournament.pref('team_standings_precedence')
        self.check_required_metrics(metrics)

        generator = TeamStandingsGenerator(metrics, self.rankings)
        generated = generator.generate(self.team_queryset)
        self.standings = list(generated)

    def filter_eligible_teams(self):
        """Places the eligible TeamStandingInfo objects in
        `self.eligible_teams`, and notes teams that are ineligible for this
        break by adding them to `self.excluded_teams`.

        Most subclasses shouldn't need to modify this method. Specifically, it
        excludes the following:
         - teams that have an existing remark (marked with remark None to
           indicate it shouldn't change)
         - teams not eligible for this break category (if it is a general
           category)
         - teams that broke in a higher-priority break

        The purpose of this method is to catch teams that shouldn't even be
        considered for the break. It's not intended to cover cases where teams
        are ruled out due to other teams in the break, for example, the AIDA
        institution cap. Such cases should be accounted for directly in the
        `compute_break()` method.
        """
        existing_remark_teams = self.team_queryset.filter(
            breakingteam__break_category=self.category,
            breakingteam__remark__isnull=False
        )
        different_break_teams = self.team_queryset.filter(
            breakingteam__break_category__priority__gt=self.category.priority
        )
        ineligible_teams = self.team_queryset.exclude(break_categories=self.category)

        self.excluded_teams = {}
        self.eligible_teams = []

        for tsi in self.standings:
            if tsi.team in existing_remark_teams:
                self.excluded_teams[tsi] = None
            elif tsi.team in ineligible_teams:
                self.excluded_teams[tsi] = BreakingTeam.REMARK_INELIGIBLE
            elif tsi.team in different_break_teams:
                self.excluded_teams[tsi] = BreakingTeam.REMARK_DIFFERENT_BREAK
            else:
                self.eligible_teams.append(tsi)

    def compute_break(self):
        """Subclasses must implement this method. It must populate
        `self.breaking_teams` with a list of TeamStandingInfo objects, each one
        being a breaking team in ranked order. If it excludes any teams from
        the break that otherwise would have broken, it should add those teams
        to `self.excluded_teams`.

        The implementation work from (a copy of) `self.eligible_teams`; i.e.,
        the breaking teams should be subset of eligible teams, and it should
        retrieve the break size from `self.break_size`. It should include in
        `self.breaking_teams` all teams that are tied in the last breaking place
        (e.g. if 16 teams break and two teams are tied 16th equal, the list
        should have 17 teams).

        If this method sets `self.hide_excluded_teams_from` to an integer, then
        `populate_database()` will not populate the database with any excluded
        teams whose overall rank is lower than `self.hide_excluded_teams_from`.
        If no excluded teams should be shown, this should be set to 0.

        If this method sets `self.break_rank_correction` to a tuple, whose
        first element is a TeamStandingInfo object and whose second element
        is an integer, then when `populate_database()` passes the given
        TeamStandingInfo object, it will subtract the integer from the break
        rank. This should be used when too many teams must be reinserted into
        the break because they are tied.
        """
        raise NotImplementedError("Subclasses must implement compute_break()")

    def populate_database(self):
        """Populates the database with BreakingTeam instances for each team
        representing in `self.breaking_teams`, and those teams in
        `self.excluded_teams` that ranked ahead of the last breaking team."""

        # We could bulk retrieve and create to reduce SQL queries, but this is a
        # rare action and the code's much easier to read using
        # update_or_create().

        # first, breaking teams
        break_rank = 1
        for rank, group in groupby(self.breaking_teams, key=lambda tsi: tsi.get_ranking("rank")):
            group = list(group)
            for tsi in group:
                BreakingTeam.objects.update_or_create(
                    break_category=self.category, team=tsi.team,
                    defaults={'rank': rank, 'break_rank': break_rank, 'remark': None}
                )
                logger.info("Breaking in %s (rank %s): %s", break_rank, rank, tsi.team)
            break_rank += len(group)

            if hasattr(self, "break_rank_correction"):
                tsi_to_apply_correction, excess = self.break_rank_correction
                if tsi_to_apply_correction in group:
                    break_rank -= excess

        # then, excluded teams
        if not hasattr(self, 'hide_excluded_teams_from'):
            self.hide_excluded_teams_from = rank

        for tsi, remark in self.excluded_teams.items():
            rank = tsi.get_ranking("rank")
            if rank < self.hide_excluded_teams_from:
                bt, _ = BreakingTeam.objects.update_or_create(
                    break_category=self.category, team=tsi.team,
                    defaults={'rank': tsi.get_ranking("rank"), 'break_rank': None, 'remark': remark}
                )
                logger.info("Excluded from break (%s, %s): %s", rank, bt.get_remark_display(), tsi.team)


class StandardBreakGenerator(BaseBreakGenerator):
    name = "Standard"
    key = "standard"
    rankings = ('rank',)

    def compute_break(self):
        self.breaking_teams = self.eligible_teams[:self.break_size]

        # If the last spot is tied, add all tied teams
        last_rank = self.eligible_teams[self.break_size-1].get_ranking("rank")
        for tsi in self.eligible[self.break_size:]:
            if tsi.get_ranking("rank") != last_rank:
                break
            self.breaking_teams.append(tsi)


class BaseAidaBreakGenerator(StandardBreakGenerator):
    name = None
    key = None
    rankings = ('rank', 'institution')
    institution_cap = 3

    def compute_break(self):
        self.exclude_capped_teams()
        super().compute_break()

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""
        raise NotImplementedError


class AidaPre2015BreakGenerator(BaseAidaBreakGenerator):
    name = "AIDA Pre-2015"
    key = "aida-pre2015"

    def compute_break(self):
        self.exclude_capped_teams()
        super().compute_break()

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""

        self.capped_teams = []

        for tsi in self.eligible_teams:
            institution_rank = tsi.get_ranking("institution")
            if institution_rank > self.institution_cap:
                logger.info("Capped out, institution rank %d, cap %d: %s", institution_rank, self.institution_cap, tsi.team)
                self.capped_teams.append(tsi)

        for tsi in self.capped_teams:
            self.eligible_teams.remove(tsi)
            self.excluded_teams[tsi] = BreakingTeam.REMARK_CAPPED


class BaseAida2016BreakGenerator(BaseAidaBreakGenerator):
    required_metrics = ('wins',)

    def exclude_capped_teams(self):
        """Excludes teams that are subject to the institution cap."""

        if len(self.eligible_teams) < self.break_size:
            return

        # ii. Discard teams with fewer wins than the nth ranked team
        min_wins = self.eligible_teams[self.break_size-1].metrics["wins"]
        self.eligible_teams = [tsi for tsi in self.eligible_teams if tsi.metrics["wins"] >= min_wins]

        # natural_break_cutoff is the (true) rank of the last breaking team,
        # not allowing for the cap but allowing for ineligible teams.
        natural_break_cutoff = self.eligible_teams[self.break_size-1].get_ranking("rank")
        self.capped_teams = []

        # iii. Set aside teams that are capped out
        for tsi in self.eligible_teams:
            institution_rank = tsi.get_ranking("institution")
            if institution_rank > 1 and tsi.get_ranking("rank") > natural_break_cutoff:
                logger.info("Capped out post-cutoff, institution rank %d: %s", institution_rank, tsi.team)
                self.capped_teams.append(tsi)
            elif institution_rank > self.institution_cap:
                logger.info("Capped out pre-cutoff, institution rank %d, cap %d: %s", institution_rank, self.institution_cap, tsi.team)
                self.capped_teams.append(tsi)

        # iv. Reinsert capped teams if there are too few breaking
        # Easters and Australs have different procedures for reinsertion.
        self.reinsert_capped_teams()

        # Now, exclude capped teams accordingly
        for tsi in self.capped_teams:
            self.eligible_teams.remove(tsi)
            self.excluded_teams[tsi] = BreakingTeam.REMARK_CAPPED

    def reinsert_capped_teams(self):
        """Unexcludes teams that were subject to the post-cutoff cap if there
        are too few teams breaking."""
        raise NotImplementedError

    def _reinsert_capped_teams(self, teams_eligible_for_reinsertion):
        """Used by subclasses to implement self.reinsert_capped_teams()"""

        if len(self.eligible_teams) - len(self.capped_teams) >= self.break_size:
            return

        reinsert = []
        number_to_reinsert = self.break_size - len(self.eligible_teams) + len(self.capped_teams)

        for _, group in groupby(teams_eligible_for_reinsertion, key=lambda tsi: tuple(tsi.itermetrics())):
            group = list(group)
            reinsert.extend(group)
            logger.info("Reinserting: %s", group)
            if len(reinsert) >= number_to_reinsert:
                tsi = group[-1]
                excess = len(reinsert) - number_to_reinsert
                logger.info("Break rank correction: %d at %s", excess, tsi.team)
                self.break_rank_correction = tsi, excess
                break

        for tsi in reinsert:
            self.capped_teams.remove(tsi)


class Aida2016EastersBreakGenerator(BaseAidaBreakGenerator):
    name = "AIDA 2016 (Easters)"
    key = "aida-2016-easters"

    def reinsert_capped_teams(self):
        # Easters rules give teams capped out post-cutoff priority
        post_cutoff_capped_teams = [tsi for tsi in self.capped_teams
            if tsi.get_ranking("institution") <= self.institution_cap]
        self._reinsert_capped_teams(post_cutoff_capped_teams)
        self._reinsert_capped_teams(self.capped_teams)


class Aida2016AustralsBreakGenerator(BaseAidaBreakGenerator):
    name = "AIDA 2016 (Australs)"
    key = "aida-2016-australs"

    def reinsert_capped_teams(self):
        self._reinsert_capped_teams(self.capped_teams)


class WadlDivisionWinnersFirstBreakGenerator(BaseBreakGenerator):
    name = "WADL (division winners first)"
    key = "wadldivfirst"


class WadlDivisionWinnersGuaranteedBreakGenerator(BaseBreakGenerator):
    name = "WADL (division winners guaranteed)"
    key = "wadl-divguaranteed"
