"""Base class and registry for break generators, and the standard break
generator (which just takes the top teams)."""

import logging
from itertools import groupby

from django.utils.encoding import force_str
from django.utils.translation import gettext as _

from breakqual.models import BreakingTeam
from standings.teams import TeamStandingsGenerator

logger = logging.getLogger(__name__)

registry = {}


def register(cls):
    registry[cls.key] = cls
    return cls


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

    2. `retrieve_standings()`, which sets `self.standings` to a Standings
       object. This function uses the metrics set in the tournament preferences,
       and the rankings specified in the `rankings` class attribute.

    3. `filter_eligible_teams()`, which sets `self.excluded_teams` to a dict
       mapping StandingInfo objects to BreakingTeam.REMARK_* constants, and sets
       `self.eligible_teams` to a list of StandingInfo objects for eligible
       teams, in the same order as they were found in `self.standings`.

    4. `compute_break()`, which sets `self.breaking_teams` to a list of
       StandingInfo objects, corresponding to the breaking teams (in order).
       Subclasses must implement this method.

    5. `populate_database()`, which writes the computed break and excluded teams
       to the database.
    """

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
                    name = annotator_class.choice_name
                else:
                    name = annotator_class.name
                return force_str(name)

            raise BreakGeneratorError(
                _("The break qualification rule %(rule)s requires the following "
                "metric(s) to be in the team standings precedence in order to "
                "work: %(required)s; and the following are missing: "
                "%(missing)s.") % {
                    'rule': self.category.get_rule_display(),
                    'required': ", ".join(_metric_name(metric) for metric in self.required_metrics),
                    'missing': ", ".join(_metric_name(metric) for metric in missing_metrics),
                },
            )

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
        """Places the eligible StandingInfo objects in
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
            breakingteam__remark__isnull=False,
        ).exclude(breakingteam__remark__exact='')
        different_break_teams = self.team_queryset.exclude(
            breakingteam__remark=BreakingTeam.REMARK_INELIGIBLE,
            breakingteam__break_category__priority__gt=self.category.priority,
        ).filter(
            breakingteam__break_category__priority__gt=self.category.priority,
        )
        ineligible_teams = self.team_queryset.exclude(break_categories=self.category)

        self.excluded_teams = {}
        self.eligible_teams = []

        for tsi in self.standings:
            if tsi.team in existing_remark_teams:
                logger.debug("Excluding %s because it has an existing remark", tsi.team)
                self.excluded_teams[tsi] = None
            elif tsi.team in ineligible_teams:
                logger.debug("Excluding %s because it is ineligible", tsi.team)
                self.excluded_teams[tsi] = BreakingTeam.REMARK_INELIGIBLE
            elif tsi.team in different_break_teams:
                logger.debug("Excluding %s because it broke in a different break", tsi.team)
                self.excluded_teams[tsi] = BreakingTeam.REMARK_DIFFERENT_BREAK
            else:
                self.eligible_teams.append(tsi)

    def compute_break(self):
        """Subclasses must implement this method. It must populate
        `self.breaking_teams` with a list of StandingInfo objects, each one
        being a breaking team in ranked order. If it excludes any teams from the
        break that otherwise would have broken, it should add those teams to
        `self.excluded_teams`.

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

        If this method sets `self.break_rank_correction` to a tuple, whose first
        element is a StandingInfo object and whose second element is an integer,
        then when `populate_database()` passes the given StandingInfo object, it
        will subtract the integer from the break rank. This should be used when
        too many teams must be reinserted into
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

        bts_to_keep = []

        # first, breaking teams
        break_rank = 1
        rank = 0 # rank is referenced after the loop, so initialize first
        for rank, group in groupby(self.breaking_teams, key=lambda tsi: tsi.get_ranking("rank")):
            group = list(group)
            for tsi in group:
                bt, _ = BreakingTeam.objects.update_or_create(
                    break_category=self.category, team=tsi.team,
                    defaults={'rank': rank, 'break_rank': break_rank, 'remark': None},
                )
                bts_to_keep.append(bt.id)
                logger.info("Breaking in %s (rank %s): %s", bt.break_rank, rank, bt.team)
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
                defaults = {'rank': tsi.get_ranking("rank"), 'break_rank': None}
                if remark is not None:
                    defaults['remark'] = remark
                bt, _ = BreakingTeam.objects.update_or_create(
                    break_category=self.category, team=tsi.team, defaults=defaults)
                bts_to_keep.append(bt.id)
                logger.info("Excluded from break (%s, %s): %s", bt.rank, bt.get_remark_display(), bt.team)

        # finally, delete stray BreakingTeam objects
        self.category.breakingteam_set.exclude(id__in=bts_to_keep).delete()


@register
class StandardBreakGenerator(BaseBreakGenerator):
    key = "standard"
    rankings = ('rank',)

    def compute_break(self):
        self.breaking_teams = self.eligible_teams[:self.break_size]

        # If the last spot is tied, add all tied teams
        if len(self.eligible_teams) >= self.break_size:
            last_rank = self.eligible_teams[self.break_size-1].get_ranking("rank")
            for tsi in self.eligible_teams[self.break_size:]:
                if tsi.get_ranking("rank") != last_rank:
                    break
                self.breaking_teams.append(tsi)
