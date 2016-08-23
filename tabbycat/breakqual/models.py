from django.db import models
from django.core.validators import MinValueValidator


class BreakCategory(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament')
    name = models.CharField(max_length=50, help_text="Name to be displayed, e.g., \"ESL\"")
    slug = models.SlugField(help_text="Slug for URLs, e.g., \"esl\"")
    seq = models.IntegerField(help_text="The order in which the categories are displayed")
    break_size = models.IntegerField(help_text="Number of breaking teams in this category", validators=[MinValueValidator(2)])
    is_general = models.BooleanField(
        help_text="True if most teams eligible for this category, e.g. Open, False otherwise")
    priority = models.IntegerField(
        help_text="If a team breaks in multiple categories, higher priority "
        "numbers take precedence; teams can break into multiple categories if "
        "and only if they all have the same priority")

    BREAK_QUALIFICATION_CHOICES = [
        ('standard', "Standard"),
        ('aida-pre2015', "AIDA Pre-2015"),
        ('aida-2016-easters', "AIDA 2016 (Easters)"),
        ('aida-2016-australs', "AIDA 2016 (Australs)"),
        ('wadl-div-first', "WADL division winners first"),
        ('wadl-div-guaranteed', "WADL division winners guaranteed"),
    ]

    rule = models.CharField(max_length=25, choices=BREAK_QUALIFICATION_CHOICES, default='standard',
        help_text="Rule for how the break is calculated (most tournaments should use \"Standard\")")

    breaking_teams = models.ManyToManyField('participants.Team', through='BreakingTeam')

    def __str__(self):
        return "[{}] {}".format(self.tournament.slug, self.name)

    class Meta:
        unique_together = [('tournament', 'seq'), ('tournament', 'slug')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']
        verbose_name_plural = "break categories"


class BreakingTeam(models.Model):
    break_category = models.ForeignKey(BreakCategory)
    team = models.ForeignKey('participants.Team')
    rank = models.IntegerField()
    break_rank = models.IntegerField(blank=True, null=True)

    REMARK_CAPPED = 'C'
    REMARK_INELIGIBLE = 'I'
    REMARK_DIFFERENT_BREAK = 'D'
    REMARK_DISQUALIFIED = 'd'
    REMARK_LOST_COIN_TOSS = 't'
    REMARK_WITHDRAWN = 'w'
    REMARK_CHOICES = ((REMARK_CAPPED, 'Capped'),
                      (REMARK_INELIGIBLE, 'Ineligible'),
                      (REMARK_DIFFERENT_BREAK, 'Different break'),
                      (REMARK_DISQUALIFIED, 'Disqualified'),
                      (REMARK_LOST_COIN_TOSS, 'Lost coin toss'),
                      (REMARK_WITHDRAWN, 'Withdrawn'), )
    remark = models.CharField(
        max_length=1,
        choices=REMARK_CHOICES,
        blank=True,
        null=True,
        help_text="Used to explain why an otherwise-qualified team didn't break")

    class Meta:
        unique_together = [('break_category', 'team')]
