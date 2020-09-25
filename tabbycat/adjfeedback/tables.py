import logging

from django.utils.translation import gettext as _, ngettext

from utils.misc import reverse_tournament
from utils.tables import TabbycatTableBuilder

from .progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam

logger = logging.getLogger(__name__)


class FeedbackTableBuilder(TabbycatTableBuilder):

    def add_breaking_checkbox(self, adjudicators, key="Breaking"):
        breaking_header = {
            'key': 'breaking',
            'icon': 'award',
            'tooltip': _("Whether the adj is marked as breaking (click to mark)"),
        }
        breaking_data = [{
            'component': 'check-cell',
            'checked':  adj.breaking ,
            'sort': adj.breaking,
            'type': 'breaking',
            'saveURL': reverse_tournament('adjfeedback-set-adj-breaking-status', self.tournament),
            'id': adj.pk,
        } for adj in adjudicators]

        self.add_column(breaking_header, breaking_data)

    @staticmethod
    def get_formatted_adj_score(score, strong=False):
        if score is None:
            return _('N/A')
        if strong is True:
            return '<strong>%0.1f</strong>' % score
        else:
            return '%0.1f' % score

    def add_weighted_score_columns(self, adjudicators, scores):
        overall_header = {
            'key': 'score',
            'icon': 'trending-up',
            'tooltip': _("Current weighted score"),
        }
        overall_data = [{
            'sort': scores[adj],
            'text': self.get_formatted_adj_score(scores[adj], True),
            'tooltip': _("This adjudicator's current rating."),
        } for adj in adjudicators]
        self.add_column(overall_header, overall_data)

    def add_base_score_columns(self, adjudicators, editable=False):
        test_header = {
            'key': 'base-score',
            'icon': 'file',
            'tooltip': _("Base score result"),
        }
        if editable:
            test_data = [{
                'text': self.get_formatted_adj_score(adj.base_score),
                'modal': adj.id,
                'class': 'edit-base-score',
                'tooltip': _("Click to edit base score"),
            } for adj in adjudicators]
        else:
            test_data = [{
                'text': self.get_formatted_adj_score(adj.base_score),
                'tooltip': _("Assigned base score"),
            } for adj in adjudicators]

        self.add_column(test_header, test_data)

    def add_score_difference_columns(self, adjudicators, scores):
        diff_header = {
            'key': 'score-difference',
            'icon': 'maximize-2',
            'tooltip': _("The current difference between an adjudicator's base score and current score"),
        }
        diff_data = [{
            'text': self.get_formatted_adj_score(scores[adj] - adj.base_score),
            'sort': scores[adj] - adj.base_score,
            'tooltip': _("The difference between this adjudicator's base score and current score"),
        } for adj in adjudicators]

        self.add_column(diff_header, diff_data)

    def add_score_variance_columns(self, adjudicators):
        diff_header = {
            'key': 'score-variance',
            'icon': 'bar-chart-2',
            'tooltip': _("The standard deviation of this adjudicator's current scores; with larger numbers meaning less consistent feedback scores."),
        }
        diff_data = [{
            'text': '%0.1f' % adj.feedback_variance if adj.feedback_variance is not None else '',
            'tooltip': _("The standard deviation of this adjudicator's current scores"),
        } for adj in adjudicators]

        self.add_column(diff_header, diff_data)

    def add_feedback_graphs(self, adjudicators):
        nprelims = self.tournament.prelim_rounds().count()
        feedback_head = {
            'key': 'feedback',
            'title': _('Feedback Per Round'),
            'tooltip': _("Hover over the data points to show the average score received in that round"),
        }
        feedback_graph_data = [{
            'graphData': adj.feedback_data,
            'component': 'feedback-trend',
            'minScore': self.tournament.pref('adj_min_score'),
            'maxScore': self.tournament.pref('adj_max_score'),
            'roundSeq': nprelims,
        } for adj in adjudicators]
        self.add_column(feedback_head, feedback_graph_data)

    def add_feedback_link_columns(self, adjudicators):
        link_head = {
            'key': 'view-feedback',
            'icon': 'eye',
        }
        link_cell = [{
            'text': ngettext(
                "View %(count)s<br>feedback",
                "View %(count)s<br>feedbacks",
                len(adj.feedback_data) - 1,
            ) % {'count': len(adj.feedback_data) - 1}, # -1 to account for base score
            'class': 'view-feedback',
            'sort': adj.debates,
            'link': reverse_tournament('adjfeedback-view-on-adjudicator', self.tournament, kwargs={'pk': adj.pk}),
        } for adj in adjudicators]
        self.add_column(link_head, link_cell)

    def add_feedback_progress_columns(self, progress_list, key="P"):
        def _owed_cell(progress):
            owed = progress.num_unsubmitted()
            cell = {
                'text': owed,
                'sort': owed,
                'class': 'text-danger strong' if owed > 0 else 'text-success',
            }
            return cell

        owed_header = {
            'key': 'owed',
            'icon': 'slash',
            'tooltip': _("Unsubmitted feedback ballots"),
        }
        owed_data = [_owed_cell(progress) for progress in progress_list]
        self.add_column(owed_header, owed_data)

        if self._show_record_links:

            def _record_link(progress):
                if isinstance(progress, FeedbackProgressForTeam):
                    url_name = 'participants-team-record' if self.admin else 'participants-public-team-record'
                    pk = progress.team.pk
                elif isinstance(progress, FeedbackProgressForAdjudicator):
                    url_name = 'participants-adjudicator-record' if self.admin else 'participants-public-adjudicator-record'
                    pk = progress.adjudicator.pk
                else:
                    logger.error("Unrecognised progress type: %s", progress.__class__.__name__)
                    return ''
                return reverse_tournament(url_name, self.tournament, kwargs={'pk': pk})

            owed_link_header = {
                'key': 'submitted',
                'icon': 'check',
            }
            owed_link_data = [{
                'text': _("View Missing Feedback"),
                'link': _record_link(progress),
            } for progress in progress_list]
            self.add_column(owed_link_header, owed_link_data)
