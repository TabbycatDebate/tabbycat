import logging
import random
from math import exp

from django.utils.translation import gettext as _, ngettext
from munkres import Munkres

from .base import AdjudicatorAllocationError, BaseAdjudicatorAllocator, register
from ..allocation import AdjudicatorAllocation

logger = logging.getLogger(__name__)


class BaseHungarianAllocator(BaseAdjudicatorAllocator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        t = self.tournament
        self.min_score = t.pref('adj_min_score')
        self.max_score = t.pref('adj_max_score')
        self.min_voting_score = t.pref('adj_min_voting_score')
        self.conflict_penalty = t.pref('adj_conflict_penalty')
        self.history_penalty = t.pref('adj_history_penalty')
        self.no_panellists = t.pref('no_panellist_position')
        self.no_trainees = t.pref('no_trainee_position')
        self.feedback_weight = self.round.feedback_weight
        self.user_warnings = []  # Surfaced to users for non-error disclosures

        self.munkres = Munkres()

    def allocate(self):
        self.populate_adj_scores(self.adjudicators)
        return self.run_allocation(), self.user_warnings

    def populate_adj_scores(self, adjudicators):
        score_min = self.min_score
        score_range = self.max_score - score_min

        for adj in adjudicators:
            adj._weighted_score = adj.weighted_score(self.feedback_weight)  # used in min_voting_score filter
            try:
                adj._normalized_score = (adj._weighted_score - score_min) / score_range * 5  # to 0-5 range
            except ZeroDivisionError:
                adj._normalized_score = 0.0

        ntoolarge = [adj._normalized_score > 5.0 for adj in adjudicators].count(True)
        if ntoolarge > 0:
            warning_msg = ngettext(
                "%(count)s score is larger than the maximum permitted adjudicator score (%(score).1f).",
                "%(count)s scores are larger than the maximum permitted adjudicator score (%(score).1f).",
                ntoolarge,
            ) % {'count': ntoolarge, 'score': self.max_score}
            self.user_warnings.append(warning_msg)
            logger.warning(warning_msg)
        ntoosmall = [adj._normalized_score < 0.0 for adj in adjudicators].count(True)
        if ntoosmall > 0:
            warning_msg = ngettext(
                "%(count)s score is smaller than the minimum permitted adjudicator score (%(score).1f).",
                "%(count)s scores are smaller than the minimum permitted adjudicator score (%(score).1f).",
                ntoosmall,
            ) % {'count': ntoosmall, 'score': self.min_score}
            self.user_warnings.append(warning_msg)
            logger.warning(warning_msg)

    def calc_cost(self, debate, adj, adjustment=0, chair=None):
        cost = 0

        # Normalise debate importances back to the 1-5 (not ±2) range expected
        normalised_importance = debate.importance + 3

        for team in debate.teams:
            cost += self.conflict_penalty * self.conflicts.conflict_adj_team(adj, team)
            cost += self.history_penalty * self.history.seen_adj_team(adj, team)
        if chair:
            cost += self.conflict_penalty * self.conflicts.conflict_adj_adj(adj, chair)
            cost += self.history_penalty * self.history.seen_adj_adj(adj, chair)

        impt = normalised_importance + adjustment
        diff = 5 + impt - adj._normalized_score
        if diff > 0.25:
            cost += 1000 * exp(diff - 0.25)

        cost += self.max_score - adj._normalized_score

        return cost

    def allocate_trainees(self, trainees, allocation, debates):
        if len(trainees) > 0 and len(debates) > 0:
            allocation_by_debate = {aa.container: aa for aa in allocation}

            logger.info("costing trainees")
            cost_matrix = []
            for debate in debates:
                chair = allocation_by_debate[debate].chair
                row = [self.calc_cost(debate, adj, adjustment=-2.0, chair=chair) for adj in trainees]
                cost_matrix.append(row)

            logger.info("optimizing trainees (matrix size: %d positions by %d trainees)", len(cost_matrix), len(cost_matrix[0]))
            indices = self.munkres.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indices)
            logger.info('total cost for %d trainees: %f', len(indices), total_cost)

            result = ((debates[i], trainees[j]) for i, j in indices if i < len(debates))
            for debate, trainee in result:
                allocation_by_debate[debate].trainees.append(trainee)
                logger.info("allocating to %s: %s (t)", debate, trainee)

    def check_matrix_exists(self, n_debates, n_voting):
        if n_voting == 0:
            info = _("There are no adjudicators eligible to be a chair or "
                     "panellist. Try changing the \"Minimum feedback score "
                     "required to be allocated as chair or panellist\" setting "
                     "to something lower than at least some adjudicators' "
                     "current scores, and try again.")
            logger.info("No adjudicators able to panel or chair")
            raise AdjudicatorAllocationError(info)
        if n_debates == 0:
            info = _("There are no debates for this round. "
                     "Maybe you haven't created a draw yet?")
            logger.info("No debates available for allocator")
            raise AdjudicatorAllocationError(info)


@register
class VotingHungarianAllocator(BaseHungarianAllocator):

    key = "hungarian-voting"

    def run_allocation(self):

        # Sort voting adjudicators in descending order by score
        voting = [a for a in self.adjudicators if a._weighted_score >= self.min_voting_score and not a.trainee]
        random.shuffle(voting)
        voting.sort(key=lambda a: a._normalized_score, reverse=True)

        # Divide into solos, panellists and trainees
        n_debates = len(self.debates)
        n_voting = len(voting)

        self.check_matrix_exists(n_debates, n_voting)

        if self.no_panellists:
            solos = voting[:n_debates]
            panellists = []
        else:
            n_expected_solos = max(n_debates - (n_voting - n_debates) // 2, 0)
            solos = voting[:n_expected_solos]
            panellists = voting[n_expected_solos:]

        if self.no_trainees:
            trainees = []
        else:
            trainees = [a for a in self.adjudicators if a not in voting]
            trainees.sort(key=lambda a: a._normalized_score, reverse=True)

        # Divide debates into solo-chaired debates and panel debates
        debates_sorted = sorted(self.debates, key=lambda d: (-d.importance, d.room_rank))
        solo_debates = debates_sorted[:len(solos)]
        panel_debates = debates_sorted[len(solos):]

        logger.info("There are %d debates (%d solo, %d panel), %d solos, %d panellists "
                "(including chairs) and %d trainees.", len(debates_sorted), len(solo_debates),
                len(panel_debates), len(solos), len(panellists), len(trainees))
        if n_voting < n_debates:
            warning_msg = _("There are %(debate_count)s debates but only %(adj_count)s "
                    "voting adjudicators.") % {'debate_count': n_debates, 'adj_count': n_voting}
            self.user_warnings.append(warning_msg)
            logger.warning(warning_msg)

        if len(panellists) < len(panel_debates) * 3:
            warning_msg = _("There are %(panel_debates)s panel debates but only %(panellists)s "
                    "available panellists (less than %(needed)s).") % {
                        'panel_debates': len(panel_debates),
                        'panellists': len(panellists),
                        'needed': len(panel_debates) * 3,
                    }
            self.user_warnings.append(warning_msg)
            logger.warning(warning_msg)

        if len(solos) > 0 and len(solo_debates) > 0:
            logger.info("costing solos")
            cost_matrix = []
            for debate in solo_debates:
                row = [self.calc_cost(debate, adj) for adj in solos]
                cost_matrix.append(row)

            logger.info("optimizing solos (matrix size: %d positions by %d adjudicators)", len(cost_matrix), len(cost_matrix[0]))
            indices = self.munkres.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indices)
            logger.info('total cost for %d solo debates: %f', len(solos), total_cost)

            result = ((solo_debates[i], solos[j]) for i, j in indices if i < len(solo_debates))
            alloc = [AdjudicatorAllocation(d, c) for d, c in result]
            for aa in alloc:
                logger.info("allocating to %s: %s", aa.container, aa.chair)

        else:
            logger.info("No solo adjudicators.")
            alloc = []

        # Allocate panellists
        if len(panellists) > 0 and len(panel_debates) > 0:
            logger.info("costing panellists")
            cost_matrix = []
            for i, debate in enumerate(panel_debates):
                for j in range(3):
                    # for the top half of these debates, the final panellist
                    # can be of lower quality than the other 2
                    adjustment = -1.0 if i < len(panel_debates)/2 and j == 2 else 0.0
                    row = [self.calc_cost(debate, adj, adjustment) for adj in panellists]
                    cost_matrix.append(row)

            logger.info("optimizing panellists (matrix size: %d positions by %d adjudicators)", len(cost_matrix), len(cost_matrix[0]))
            indices = self.munkres.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indices)
            logger.info('total cost for %d panel debates: %f', len(panel_debates), total_cost)

            # transfer the indices to the debates
            # the debate corresponding to row r is floor(r/3) (i.e. r // 3)
            n = len(panel_debates)
            panels = [[] for i in range(n)]
            for r, c in indices[:n*3]:
                panels[r // 3].append(panellists[c])

            # create the corresponding adjudicator allocations, making sure that
            # the chair is the highest-ranked adjudicator in the panel
            for i, debate in enumerate(panel_debates):
                aa = AdjudicatorAllocation(debate)
                panels[i].sort(key=lambda a: a._normalized_score, reverse=True)
                if not panels[i]:
                    continue
                aa.chair = panels[i].pop(0)
                aa.panellists = panels[i]
                alloc.append(aa)

        for aa in alloc[len(solos):]:
            logger.info("allocating to %s: %s (c), %s", aa.container, aa.chair, ", ".join([str(p) for p in aa.panellists]))

        # Allocate trainees, one per solo debate (leave the rest unallocated)
        self.allocate_trainees(trainees, alloc, solo_debates)

        return alloc


@register
class ConsensusHungarianAllocator(BaseHungarianAllocator):

    key = "hungarian-consensus"

    def run_allocation(self):

        # Sort voting adjudicators in descending order by score
        voting = [a for a in self.adjudicators if a._weighted_score >= self.min_voting_score and not a.trainee]
        random.shuffle(voting)
        voting.sort(key=lambda a: a._normalized_score, reverse=True)

        n_debates = len(self.debates)
        if self.no_panellists:
            voting = voting[:n_debates]
        n_voting = len(voting)

        if self.no_trainees:
            trainees = []
        else:
            trainees = [a for a in self.adjudicators if a not in voting]
            trainees.sort(key=lambda a: a._normalized_score, reverse=True)

        self.check_matrix_exists(n_debates, n_voting)

        # Divide debates into solo-chaired debates and panel debates
        debates_sorted = sorted(self.debates, key=lambda d: (-d.importance, d.room_rank))

        # Figure out how many judges per room, prioritising the most important
        judges_per_room_floor = n_voting // n_debates
        n_bigger_panels = n_voting % n_debates
        judges_per_room = [judges_per_room_floor+1] * n_bigger_panels + [judges_per_room_floor] * (n_debates - n_bigger_panels)

        logger.info("There are %d debates, %d voting adjudicators and %d trainees",
                len(debates_sorted), len(voting), len(trainees))
        if n_voting < n_debates:
            warning_msg = _("There are %(debates_count)s debates but only "
                    "%(voting_count)s voting adjudicators.") % {
                        'debates_count': n_debates,
                        'voting_count': n_voting,
                    }
            self.user_warnings.append(warning_msg)
            logger.warning(warning_msg)

        # Allocate voting
        logger.info("costing voting adjudicators")
        cost_matrix = []
        for debate, njudges in zip(debates_sorted, judges_per_room):
            for i in range(njudges):
                row = [self.calc_cost(debate, adj, adjustment=-i) for adj in voting]
                cost_matrix.append(row)

        logger.info("optimizing voting adjudicators (matrix size: %d positions by %d adjudicators)",
                len(cost_matrix), len(cost_matrix[0]))
        indices = self.munkres.compute(cost_matrix)
        indices.sort()
        total_cost = sum(cost_matrix[i][j] for i, j in indices)
        logger.info('total cost for %d debates: %f', n_debates, total_cost)

        # transfer the indices to the debates
        alloc = []
        for debate, njudges in zip(debates_sorted, judges_per_room):
            aa = AdjudicatorAllocation(debate)
            panel_indices = indices[0:njudges]
            panel = [voting[c] for r, c in panel_indices]
            panel.sort(key=lambda a: a._normalized_score, reverse=True)
            try:
                aa.chair = panel.pop(0)
            except IndexError:
                aa.chair = None
            aa.panellists = panel
            alloc.append(aa)
            del indices[0:njudges]

            logger.info("allocating to %s: %s (c), %s", aa.container, aa.chair, ", ".join([str(p) for p in aa.panellists]))

        # Allocate trainees
        self.allocate_trainees(trainees, alloc, debates_sorted)

        return alloc
