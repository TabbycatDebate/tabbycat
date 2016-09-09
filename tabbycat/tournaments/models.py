from warnings import warn

from django.db import models
from django.db.models import Count, signals
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property

from participants.emoji import EMOJI_LIST
from utils.managers import LookupByNameFieldsMixin

import logging
logger = logging.getLogger(__name__)


PROHIBITED_TOURNAMENT_SLUGS = [
    'jet', 'database', 'admin', 'accounts',   # System
    'start', 'create',  # Setup Wizards
    'draw', 'participants', 'favicon.ico',  # Cross-Tournament app's view roots
    't', '__debug__', 'static']  # Misc

def validate_tournament_slug(value):
    if value in PROHIBITED_TOURNAMENT_SLUGS:
        raise ValidationError(
            "You can't use any of the following as tournament slugs, because "
            "they're reserved for Tabbycat system URLs: %(prohibited_list)s.",
            params={'prohibited_list': ", ".join(PROHIBITED_TOURNAMENT_SLUGS)}
        )


class Tournament(models.Model):
    name = models.CharField(max_length=100,
        help_text="The full name used on the homepage, e.g. \"Australasian Intervarsity Debating Championships 2016\"")
    short_name = models.CharField(max_length=25, blank=True, null=True, default="",
        help_text="The name used in the menu, e.g. \"Australs 2016\"")
    emoji = models.CharField(max_length=2, blank=True, null=True, unique=True, choices=EMOJI_LIST)
    seq = models.IntegerField(blank=True, null=True,
        help_text="A number that determines the relative order in which tournaments are displayed on the homepage.")
    slug = models.SlugField(unique=True, validators=[validate_tournament_slug],
        help_text="The sub-URL of the tournament, cannot have spaces, e.g. \"australs2016\"")
    current_round = models.ForeignKey('Round', null=True, blank=True, related_name='tournament_',
        help_text="Must be set for the tournament to start! (Set after rounds are inputted)")
    welcome_msg = models.TextField(blank=True, null=True, default="",
        help_text="Text/html entered here shows on the homepage for this tournament")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['seq', ]

    def __init__(self, *args, **kwargs):
        self._prefs = {}
        return super().__init__(*args, **kwargs)

    def __str__(self):
        if self.short_name:
            return str(self.short_name)
        else:
            return str(self.name)

    # --------------------------------------------------------------------------
    # Properties related to preferences
    # --------------------------------------------------------------------------

    def pref(self, name):
        try:
            return self._prefs[name]
        except KeyError:
            self._prefs[name] = self.preferences.get_by_name(name)
            return self._prefs[name]

    @property
    def LAST_SUBSTANTIVE_POSITION(self):  # flake8: noqa
        """Returns the number of substantive speakers."""
        return self.pref('substantive_speakers')

    @property
    def REPLY_POSITION(self):  # flake8: noqa
        """If there is a reply position, returns one more than the number of
        substantive speakers. If there is no reply position, returns None."""
        if self.pref('reply_scores_enabled'):
            return self.pref('substantive_speakers') + 1
        else:
            return None

    @property
    def POSITIONS(self):  # flake8: noqa
        """Guaranteed to be consecutive numbers starting at one. Includes the
        reply speaker."""
        speaker_positions = 1 + self.pref('substantive_speakers')
        if self.pref('reply_scores_enabled') is True:
            speaker_positions = speaker_positions + 1
        return list(range(1, speaker_positions))

    # --------------------------------------------------------------------------
    # Permalinks
    # --------------------------------------------------------------------------

    @models.permalink
    def get_absolute_url(self):
        return ('tournament-admin-home', [self.slug])

    @models.permalink
    def get_public_url(self):
        return ('tournament-public-index', [self.slug])

    # --------------------------------------------------------------------------
    # Convenience querysets
    # --------------------------------------------------------------------------

    @cached_property
    def teams(self):
        warn('Tournament.teams is deprecated, use Tournament.team_set instead.', stacklevel=2)
        return self.team_set

    @property
    def relevant_adjudicators(self):
        """Convenience property for retrieving adjudicators relevant to the tournament.
        Returns a QuerySet."""
        if self.pref('share_adjs'):
            return Adjudicator.objects.filter(Q(tournament=self) | Q(tournament__isnull=True))
        else:
            return self.adjudicator_set.all()

    @property
    def relevant_venues(self):
        """Convenience property for retrieving venues relevant to the tournament.
        Returns a QuerySet."""
        if self.pref('share_adjs'):
            return Venue.objects.filter(Q(tournament=self) | Q(tournament__isnull=True))
        else:
            return self.venue_set.all()

    def prelim_rounds(self, before=None, until=None):
        """Convenience function for retrieving preliminary rounds. Returns a QuerySet."""
        qs = self.round_set.filter(stage=Round.STAGE_PRELIMINARY)
        if until:
            qs = qs.filter(seq__lte=until.seq)
        if before:
            qs = qs.filter(seq__lt=before.seq)
        return qs

    def break_rounds(self):
        """Convenience function for retrieving break rounds. Returns a QuerySet."""
        return self.round_set.filter(stage=Round.STAGE_ELIMINATION)

    @cached_property
    def adj_feedback_questions(self):
        return self.adjudicatorfeedbackquestion_set.order_by("seq")

    # --------------------------------------------------------------------------
    # Cached
    # --------------------------------------------------------------------------

    @cached_property
    def get_current_round_cached(self):
        cached_key = "%s_current_round_object" % self.slug
        if self.current_round:
            cache.get_or_set(cached_key, self.current_round, None)
            return cache.get(cached_key)
        else:
            return None

    # --------------------------------------------------------------------------
    # Operations that modify the instance
    # --------------------------------------------------------------------------

    def advance_round(self):
        next_round_seq = self.current_round.seq + 1
        next_round = Round.objects.get(seq=next_round_seq, tournament=self)
        self.current_round = next_round
        self.save()


def update_tournament_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s" % (instance.slug, 'object')
    cache.delete(cached_key)
    cached_key = "%s_%s" % (instance.slug, 'current_round_object')
    cache.delete(cached_key)

# Update the cached tournament object when model is changed)
signals.post_save.connect(update_tournament_cache, sender=Tournament)


class RoundManager(LookupByNameFieldsMixin, models.Manager):
    use_for_related_fields = True
    name_fields = ['name', 'abbreviation']

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').order_by('seq')


class Round(models.Model):
    DRAW_RANDOM = 'R'
    DRAW_MANUAL = 'M'
    DRAW_ROUNDROBIN = 'D'
    DRAW_POWERPAIRED = 'P'
    DRAW_FIRSTBREAK = 'F'
    DRAW_BREAK = 'B'
    DRAW_CHOICES = ((DRAW_RANDOM, 'Random'),
                    (DRAW_MANUAL, 'Manual'),
                    (DRAW_ROUNDROBIN, 'Round-robin'),
                    (DRAW_POWERPAIRED, 'Power-paired'),
                    (DRAW_FIRSTBREAK, 'First elimination'),
                    (DRAW_BREAK, 'Subsequent elimination'), )

    STAGE_PRELIMINARY = 'P'
    STAGE_ELIMINATION = 'E'
    STAGE_CHOICES = ((STAGE_PRELIMINARY, 'Preliminary'),
                     (STAGE_ELIMINATION, 'Elimination'), )

    VALID_DRAW_TYPES_BY_STAGE = {
        STAGE_PRELIMINARY: [DRAW_RANDOM, DRAW_MANUAL, DRAW_ROUNDROBIN, DRAW_POWERPAIRED],
        STAGE_ELIMINATION: [DRAW_FIRSTBREAK, DRAW_BREAK],
    }

    STATUS_NONE = 'N'
    STATUS_DRAFT = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_RELEASED = 'R'
    STATUS_CHOICES = ((STATUS_NONE, 'None'),
                      (STATUS_DRAFT, 'Draft'),
                      (STATUS_CONFIRMED, 'Confirmed'),
                      (STATUS_RELEASED, 'Released'), )

    objects = RoundManager()

    tournament = models.ForeignKey(Tournament)
    seq = models.IntegerField(help_text="A number that determines the order of the round, IE 1 for the initial round")
    name = models.CharField(max_length=40, help_text="e.g. \"Round 1\"")
    abbreviation = models.CharField(max_length=10, help_text="e.g. \"R1\"")
    draw_type = models.CharField(max_length=1, choices=DRAW_CHOICES,
        help_text="Which draw technique to use")
    stage = models.CharField(max_length=1, choices=STAGE_CHOICES, default=STAGE_PRELIMINARY,
        help_text="Preliminary = inrounds, elimination = outrounds")
    break_category = models.ForeignKey('breakqual.BreakCategory', blank=True, null=True,
        help_text="If elimination round, which break category")

    draw_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE,
       help_text="The status of this round's draw")

    checkins = models.ManyToManyField('participants.Person', through='availability.Checkin', related_name='checkedin_rounds')
    active_venues = models.ManyToManyField('venues.Venue', through='availability.ActiveVenue')
    active_adjudicators = models.ManyToManyField('participants.Adjudicator', through='availability.ActiveAdjudicator')
    active_teams = models.ManyToManyField('participants.Team', through='availability.ActiveTeam')

    feedback_weight = models.FloatField(default=0,
        help_text="The extent to which each adjudicator's overall score depends on feedback vs their test score. At 0, it is 100% drawn from their test score, at 1 it is 100% drawn from feedback.")
    silent = models.BooleanField(default=False,
        help_text="If marked silent, information about this round (such as it's results) will not be shown publicly.")
    motions_released = models.BooleanField(default=False,
        help_text="Whether motions will appear on the public website, assuming that feature is turned on")
    starts_at = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = [('tournament', 'seq')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']

    def __str__(self):
        return "[%s] %s" % (self.tournament, self.name)

    def clean(self):
        super().clean()
        valid_draw_types = self.VALID_DRAW_TYPES_BY_STAGE[self.stage]
        if self.draw_type not in valid_draw_types:
            display_names = [name for value, name in self.DRAW_CHOICES if value in valid_draw_types]
            raise ValidationError({'draw_type': "A round in the {stage} stage must have a "
                "draw type that is one of: {valid}".format(
                    stage=self.get_stage_display().lower(),
                    valid=", ".join(display_names)
                )})

    def num_debates_without_chair(self):
        """Returns the number of debates in the round that lack a chair, or have
        more than one chair."""
        from adjallocation.models import DebateAdjudicator
        debates_in_round = self.debate_set.count()
        debates_with_one_chair = self.debate_set.filter(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR).annotate(
                num_chairs=Count('debateadjudicator')).filter(num_chairs=1).count()
        logger.debug("%d debates without chair", debates_in_round - debates_with_one_chair)
        return debates_in_round - debates_with_one_chair

    def num_debates_with_even_panel(self):
        """Returns the number of debates in the round, in which there are an
        positive and even number of voting judges."""
        from adjallocation.models import DebateAdjudicator
        debates_with_even_panel = self.debate_set.exclude(
                debateadjudicator__type=DebateAdjudicator.TYPE_TRAINEE
            ).annotate(
                panellists=Count('debateadjudicator'),
                odd_panellists=Count('debateadjudicator') % 2
            ).filter(panellists__gt=0, odd_panellists=0).count()
        logger.debug("%d debates with even panel", debates_with_even_panel)
        return debates_with_even_panel

    def num_debates_without_venue(self):
        debates_without_venue = self.debate_set.filter(venue__isnull=True).count()
        logger.debug("%d debates without venue", debates_without_venue)
        return debates_without_venue

    @cached_property
    def is_break_round(self):
        return self.stage == self.STAGE_ELIMINATION

    # ==========================================================================
    # Draw retrieval methods
    # ==========================================================================

    def get_draw(self, ordering=('venue__name',)):
        warn("Round.get_draw() is deprecated, use Round.debate_set or Round.debate_set_with_prefetches() instead.", stacklevel=2)
        related = ('venue',)
        if self.tournament.pref('enable_divisions'):
            related += ('division', 'division__venue_group')
        return self.debate_set.order_by(*ordering).select_related(*related)

    def debate_set_with_prefetches(self, filter_kwargs=None, ordering=('venue__name',),
            teams=True, adjudicators=True, speakers=True, divisions=True, ballotsubs=False,
            wins=False, ballotsets=False, venues=True, institutions=False):
        """Returns the debate set, with aff_team and neg_team populated.
        This is basically a prefetch-like operation, except that it also figures
        out which team is on which side, and sets attributes accordingly."""
        from draw.prefetch import populate_teams
        from results.prefetch import populate_confirmed_ballots, populate_wins

        debates = self.debate_set.all()
        if filter_kwargs:
            debates = debates.filter(**filter_kwargs)
        if ballotsubs or ballotsets:
            debates = debates.prefetch_related('ballotsubmission_set', 'ballotsubmission_set__submitter')
        if adjudicators:
            debates = debates.prefetch_related('debateadjudicator_set__adjudicator')
        if divisions and self.tournament.pref('enable_divisions'):
            debates = debates.select_related('division', 'division__venue_group')
        if venues:
            debates = debates.select_related('venue', 'venue__group')

        if ordering:
            debates = debates.order_by(*ordering)

        # These functions populate relevant attributes of each debate, operating in-place
        if teams or speakers or wins or institutions:
            populate_teams(debates, speakers=speakers, institutions=institutions)  # _aff_team, _aff_dt, _neg_team, _neg_dt
        if ballotsubs or ballotsets:
            populate_confirmed_ballots(debates, motions=True, ballotsets=ballotsets)
        if wins:
            populate_wins(debates)

        return debates

    # TODO: all these availability methods should be in the availability app

    def base_availability(self,
                          model,
                          active_table,
                          active_column,
                          model_table,
                          id_field='id'):
        d = {
            'active_table': active_table,
            'active_column': active_column,
            'model_table': model_table,
            'id_field': id_field,
            'id': self.id,
        }
        return model.objects.all().extra(
            select={'is_active': """EXISTS (Select 1
                                                 from %(active_table)s
                                                 drav where
                                                 drav.%(active_column)s =
                                                 %(model_table)s.%(id_field)s and
                                                 drav.round_id=%(id)d)""" % d})

    def person_availability(self):
        from participants.models import Person
        return self.base_availability(Person, 'availability_checkin',
                                      'person_id', 'participants_person')

    def venue_availability(self):
        from venues.models import Venue
        all_venues = self.base_availability(Venue, 'availability_activevenue',
                                            'venue_id', 'venues_venue')

        if self.tournament.pref('share_venues'):
            return [v for v in all_venues if v.tournament == self.tournament or v.tournament is None]
        else:
            return [v for v in all_venues if v.tournament == self.tournament]

    def unused_venues(self):
        from venues.models import Venue
        # Had to replicate venue_availability via base_availability so extra()
        # could still function on the query set
        result = self.base_availability(
            Venue, 'availability_activevenue', 'venue_id',
            'venues_venue').extra(select={'is_used': """EXISTS (SELECT 1
                                      FROM draw_debate da
                                      WHERE da.round_id=%d AND
                                      da.venue_id = venues_venue.id)""" %
                                          self.id}, )

        if self.tournament.pref('share_venues'):
            return [v for v in result if v.is_active and not v.is_used and v.tournament == self.tournament or v.tournament is None]
        else:
            return [v for v in result if v.is_active and not v.is_used and v.tournament == self.tournament]

    def adjudicator_availability(self):
        from participants.models import Adjudicator
        all_adjs = self.base_availability(Adjudicator,
                                          'availability_activeadjudicator',
                                          'adjudicator_id',
                                          'participants_adjudicator',
                                          id_field='person_ptr_id')

        if self.tournament.pref('share_adjs'):
            return [a for a in all_adjs if a.tournament == self.tournament or a.tournament is None]
        else:
            return [a for a in all_adjs if a.tournament == self.tournament]

    def unused_adjudicators(self):
        from participants.models import Adjudicator
        result = self.base_availability(
            Adjudicator,
            'availability_activeadjudicator',
            'adjudicator_id',
            'participants_adjudicator',
            id_field='person_ptr_id').extra(
                select={'is_used': """EXISTS (SELECT 1
                                                  FROM adjallocation_debateadjudicator da
                                                  LEFT JOIN draw_debate d ON da.debate_id = d.id
                                                  WHERE d.round_id = %d AND
                                                  da.adjudicator_id = participants_adjudicator.person_ptr_id)"""
                        % self.id}, )
        if not self.tournament.pref('draw_skip_adj_checkins'):
            return [a for a in result if a.is_active and not a.is_used]
        else:
            return [a for a in result if not a.is_used]

    def team_availability(self):
        from participants.models import Team
        all_teams = self.base_availability(Team, 'availability_activeteam',
                                           'team_id', 'participants_team')
        relevant_teams = [t for t in all_teams
                          if t.tournament == self.tournament]
        return relevant_teams

    def unused_teams(self):
        from draw.models import DebateTeam
        all_teams = self.active_teams.all()
        all_teams = [t for t in all_teams if t.tournament == self.tournament]

        debating_teams = [
            t.team
            for t in DebateTeam.objects.filter(
                debate__round=self).select_related('team', 'debate')
        ]
        unused_teams = [t for t in all_teams if t not in debating_teams]

        return unused_teams

    def set_available_base(self,
                           ids,
                           model,
                           active_model,
                           get_active,
                           id_column,
                           active_id_column,
                           remove=True):
        ids = set(ids)
        all_ids = set(a['id'] for a in model.objects.values('id'))
        exclude_ids = all_ids.difference(ids)
        existing_ids = set(a['id'] for a in get_active.values('id'))

        remove_ids = existing_ids.intersection(exclude_ids)
        add_ids = ids.difference(existing_ids)

        if remove:
            active_model.objects.filter(**{
                '%s__in' % active_id_column: remove_ids,
                'round': self,
            }).delete()

        for id in add_ids:
            m = active_model(round=self)
            setattr(m, id_column, id)
            m.save()


    def set_available_venues(self, ids):
        from availability.models import ActiveVenue
        from venues.models import Venue
        return self.set_available_base(ids, Venue, ActiveVenue,
                                       self.active_venues, 'venue_id',
                                       'venue__id')

    def set_available_adjudicators(self, ids):
        from availability.models import ActiveAdjudicator
        from participants.models import Adjudicator
        return self.set_available_base(ids, Adjudicator, ActiveAdjudicator,
                                       self.active_adjudicators,
                                       'adjudicator_id', 'adjudicator__id')

    def set_available_teams(self, ids):
        from availability.models import ActiveTeam
        from participants.models import Team
        return self.set_available_base(
            ids, Team, ActiveTeam, self.active_teams, 'team_id', 'team__id')

    def activate_adjudicator(self, adj, state=True):
        from availability.models import ActiveAdjudicator
        if state:
            ActiveAdjudicator.objects.get_or_create(round=self,
                                                    adjudicator=adj)
        else:
            self.activeadjudicator_set.filter(adjudicator=adj).delete()

    def activate_venue(self, venue, state=True):
        from availability.models import ActiveVenue
        if state:
            ActiveVenue.objects.get_or_create(round=self, venue=venue)
        else:
            self.activevenue_set.filter(venue=venue).delete()

    def activate_team(self, team, state=True):
        from availability.models import ActiveTeam
        if state:
            ActiveTeam.objects.get_or_create(round=self, team=team)
        else:
            self.activeteam_set.filter(team=team).delete()

    def activate_all_breaking_adjs(self):
        from participants.models import Adjudicator
        self.set_available_adjudicators(
            [a.id for a in Adjudicator.objects.filter(breaking=True)])

    def activate_all_breaking_teams(self):
        from breakqual.models import BreakingTeam
        breaking_teams = BreakingTeam.objects.filter(
            break_category=self.break_category, remark=None,
            team__tournament=self.tournament)
        self.set_available_teams([bt.team.id for bt in breaking_teams])

    def activate_all_advancing_teams(self):
        from results.models import TeamScore
        prior_break_round = Round.objects.filter(
            break_category=self.break_category, seq__lte=self.seq).exclude(
            id=self.id).order_by('-seq').first()
        prior_results = TeamScore.objects.filter(
            win=True, ballot_submission__confirmed=True,
            ballot_submission__debate__round=prior_break_round)
        self.set_available_teams([r.debate_team.team.id for r in prior_results])

    def activate_all(self):
        from venues.models import Venue
        from participants.models import Adjudicator, Team
        all_teams = Team.objects.filter(tournament=self.tournament)
        all_venues = Venue.objects.filter(tournament=self.tournament)
        all_adjs = Adjudicator.objects.filter(tournament=self.tournament)

        if self.tournament.pref('share_adjs'):
            all_adjs = all_adjs | Adjudicator.objects.filter(tournament=None)
        if self.tournament.pref('share_venues'):
            all_venues = all_venues | Venue.objects.filter(tournament=None)

        self.set_available_teams([t.id for t in all_teams])
        self.set_available_venues([v.id for v in all_venues])
        self.set_available_adjudicators([a.id for a in all_adjs])

    def activate_previous(self):
        from availability.models import ActiveTeam, ActiveAdjudicator, ActiveVenue

        self.set_available_venues(
            [v.venue.id for v in ActiveVenue.objects.filter(round=self.prev)])
        self.set_available_adjudicators(
            [a.adjudicator.id
             for a in ActiveAdjudicator.objects.filter(round=self.prev)])
        self.set_available_teams(
            [t.team.id for t in ActiveTeam.objects.filter(round=self.prev)])

    @cached_property
    def prev(self):
        try:
            return self.tournament.round_set.filter(seq__lt=self.seq).order_by('-seq').first()
        except Round.DoesNotExist:
            return None

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()


def update_round_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s_%s" % (instance.tournament.slug, instance.seq,
                               'object')
    cache.delete(cached_key)
    logger.debug("Updated cache %s for %s" % (cached_key, instance))

    if instance.tournament.current_round_id == instance.id:
        logger.debug("Updating tournament cache because %s is the current round" % instance)
        update_tournament_cache(sender, instance.tournament, False, **kwargs)

# Update the cached round object when model is changed)
signals.post_save.connect(update_round_cache, sender=Round)
