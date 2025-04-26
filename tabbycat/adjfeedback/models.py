from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _

from adjallocation.models import DebateAdjudicator
from registration.models import Answer, Question
from results.models import Submission
from utils.models import UniqueConstraint


class AdjudicatorBaseScoreHistory(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        verbose_name=_("adjudicator"))
    # cascade to avoid ambiguity, null round indicates beginning of tournament
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True,
        verbose_name=_("round"))
    score = models.FloatField(verbose_name=_("score"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"))

    class Meta:
        verbose_name = _("adjudicator base score history")
        verbose_name_plural = _("adjudicator base score histories")

    def __str__(self):
        return "{.name:s} ({:.1f}) in {!s}".format(self.adjudicator, self.score, self.round)


class AdjudicatorFeedbackQuestion(Question):

    reference = models.SlugField(
        verbose_name=_("reference"),
        help_text=_("Code-compatible reference, e.g., \"agree_with_decision\""))

    from_adj = models.BooleanField(
        verbose_name=_("from adjudicator"),
        help_text=_("Adjudicators should be asked this question (about other adjudicators)"))
    from_team = models.BooleanField(
        verbose_name=_("from team"),
        help_text=_("Teams should be asked this question"))

    class Meta:
        verbose_name = _("adjudicator feedback question")
        verbose_name_plural = _("adjudicator feedback questions")

    def serialize(self):
        question = {
            'text': escape(self.text),
            'seq': self.seq,
            'type': self.answer_type,
            'required': self.answer_type,
            'from_team': self.from_team,
            'from_adj': self.from_adj,
        }
        if self.choices:
            question['choice_options'] = [escape(c) for c in self.choices]
        elif self.min_value is not None and self.max_value is not None:
            question['choice_options'] = self.choices_for_number_scale
        return question


class AdjudicatorFeedback(Submission):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE, db_index=True,
        verbose_name=_("adjudicator"))
    score = models.FloatField(verbose_name=_("score"))

    # cascade to avoid double-null sources, each feedback must have exactly one source
    source_adjudicator = models.ForeignKey('adjallocation.DebateAdjudicator', models.CASCADE, blank=True, null=True,
        verbose_name=_("source adjudicator"))
    source_team = models.ForeignKey('draw.DebateTeam', models.CASCADE, blank=True, null=True,
        verbose_name=_("source team"))

    ignored = models.BooleanField(default=False,
        verbose_name=_("ignored"),
        help_text=_("Whether the feedback should affect the adjudicator's score"))

    answers = GenericRelation(Answer)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['adjudicator', 'source_adjudicator', 'source_team', 'version']),
        ]
        verbose_name = _("adjudicator feedback")
        verbose_name_plural = _("adjudicator feedbacks")

    def __str__(self):
        return "Feedback from {source} on {adj} submitted at {time} (version {version})".format(
            source=self.source,
            adj=self.adjudicator.name,
            version=self.version,
            time=('<unknown>' if self.timestamp is None else str(
                self.timestamp.isoformat())))

    def _unique_unconfirm_args(self):
        kwargs = super()._unique_unconfirm_args()
        if self.source_team is not None and self.source_team.debate.round.tournament.pref('feedback_from_teams') == 'orallist':
            kwargs.pop('adjudicator')
        return kwargs

    @cached_property
    def source(self):
        if self.source_adjudicator:
            return self.source_adjudicator.adjudicator.name
        if self.source_team:
            return self.source_team.team.short_name

    @cached_property
    def debate(self):
        if self.source_adjudicator:
            return self.source_adjudicator.debate
        if self.source_team:
            return self.source_team.debate

    @cached_property
    def debate_adjudicator(self):
        if not hasattr(self, '_debateadj'):
            try:
                self._debateadj = self.adjudicator.debateadjudicator_set.get(
                    debate=self.debate)
            except DebateAdjudicator.DoesNotExist:
                self._debateadj = None
        return self._debateadj

    @property
    def round(self):
        return self.debate.round

    @cached_property
    def feedback_weight(self):
        if self.round:
            return self.round.feedback_weight
        return 1

    def clean(self):
        if not (self.source_adjudicator or self.source_team):
            raise ValidationError(
                gettext("Either the source adjudicator or source team wasn't specified."))
        if self.source_adjudicator and self.source_team:
            raise ValidationError(
                gettext("There was both a source adjudicator and a source team."))
        if not self.adjudicator:
            raise ValidationError(gettext("There is no adjudicator specified as the target for this feedback. Perhaps they were deleted?"))
        if self.adjudicator not in self.debate.adjudicators:
            raise ValidationError(gettext("Adjudicator did not see this debate."))
        return super(AdjudicatorFeedback, self).clean()
