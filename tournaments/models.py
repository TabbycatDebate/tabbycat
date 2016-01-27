from django.db import models
from django.db.models import signals
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property

from participants.emoji import EMOJI_LIST
from adjallocation.anneal import SAAllocator

import logging
logger = logging.getLogger(__name__)

class Tournament(models.Model):
    name = models.CharField(max_length=100, help_text="The full name used on the homepage")
    short_name  = models.CharField(max_length=25, blank=True, null=True, default="", help_text="The name used in the menu")
    emoji = models.CharField(max_length=1, blank=True, null=True, unique=True, choices=EMOJI_LIST)
    seq = models.IntegerField(blank=True, null=True, help_text="The order in which tournaments are displayed")
    slug = models.SlugField(unique=True, help_text="The sub-URL of the tournament; cannot have spaces")
    current_round = models.ForeignKey('Round', null=True, blank=True,
                                     related_name='tournament_', help_text="Must be set for the tournament to start! (Set after rounds are inputted)")
    welcome_msg = models.TextField(blank=True, null=True, default="", help_text="Text/html entered here shows on the homepage")
    release_all = models.BooleanField(default=False, help_text="This releases all results; do so only after the tournament is finished")
    active = models.BooleanField(default=True)

    @property
    def LAST_SUBSTANTIVE_POSITION(self):
        """Returns the number of substantive speakers."""
        return self.pref('substantive_speakers')

    @property
    def REPLY_POSITION(self):
        """If there is a reply position, returns one more than the number of
        substantive speakers. If there is no reply position, returns None."""
        if self.pref('reply_scores_enabled'):
            return self.pref('substantive_speakers') + 1
        else:
            return None

    @property
    def POSITIONS(self):
        """Guaranteed to be consecutive numbers starting at one. Includes the
        reply speaker."""
        speaker_positions = 1 + self.pref('substantive_speakers')
        if self.pref('reply_scores_enabled') is True:
            speaker_positions = speaker_positions + 1
        return list(range(1, speaker_positions))

    @models.permalink
    def get_absolute_url(self):
        return ('tournament_home', [self.slug])

    @models.permalink
    def get_public_url(self):
        return ('public_index', [self.slug])

    @models.permalink
    def get_all_tournaments_all_venues(self):
        return ('all_tournaments_all_venues', [self.slug])

    @models.permalink
    def get_all_tournaments_all_institutions(self):
        return ('all_tournaments_all_institutions', [self.slug])

    @models.permalink
    def get_all_tournaments_all_teams(self):
        return ('all_tournaments_all_teams', [self.slug])

    @property
    def teams(self):
        return self.team_set

    @cached_property
    def get_current_round_cached(self):
        cached_key = "%s_current_round_object" % self.slug
        cache.get_or_set(cached_key, self.current_round, None)
        return cache.get(cached_key)

    def prelim_rounds(self, before=None, until=None):
        qs = self.round_set.filter(stage=Round.STAGE_PRELIMINARY)
        if until:
            qs = qs.filter(seq__lte=until.seq)
        if before:
            qs = qs.filter(seq__lt=before.seq)
        return qs

    def break_rounds(self):
        return self.round_set.filter(stage=Round.STAGE_ELIMINATION)

    def advance_round(self):
        next_round_seq = self.current_round.seq + 1
        next_round = Round.objects.get(seq=next_round_seq, tournament=self)
        self.current_round = next_round
        self.save()
        self.unset_current_round_cached()

    def pref(self, name):
        return self.preferences.get_by_name(name)

    @cached_property
    def config(self):
        if not hasattr(self, '_config'):
            from options.options import Config # TODO: improve the semantics here
            self._config = Config(self)
        return self._config

    @cached_property
    def adj_feedback_questions(self):
        return self.adjudicatorfeedbackquestion_set.order_by("seq")

    class Meta:
        ordering = ['seq',]
        verbose_name = "🏆 Tournament"

    def __str__(self):
        if self.short_name:
            return str(self.short_name)
        else:
            return str(self.name)

def update_tournament_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s" % (instance.slug, 'object')
    cache.delete(cached_key)
    cached_key = "%s_%s" % (instance.slug, 'current_round_object')
    cache.delete(cached_key)

# Update the cached tournament object when model is changed)
signals.post_save.connect(update_tournament_cache, sender=Tournament)


class Division(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name or suffix")
    seq = models.IntegerField(blank=True, null=True, help_text="The order in which divisions are displayed")
    tournament = models.ForeignKey(Tournament)
    time_slot = models.TimeField(blank=True, null=True)
    venue_group = models.ForeignKey('venues.VenueGroup', blank=True, null=True)

    @property
    def teams_count(self):
        return self.team_set.count()

    @cached_property
    def teams(self):
        return self.team_set.all().order_by('institution','reference').select_related('institution')

    def __str__(self):
        return "%s - %s" % (self.tournament, self.name)

    class Meta:
        unique_together = [('tournament', 'name')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']
        verbose_name = "➗ Division"


class RoundManager(models.Manager):
    use_for_related_Fields = True

    def lookup(self, name, **kwargs):
        """Queries for a round with matching name in any of the two name
        fields."""
        for field in ('name', 'abbreviation'):
            try:
                kwargs[field] = name
                return self.get(**kwargs)
            except ObjectDoesNotExist:
                kwargs.pop(field)
        raise self.model.DoesNotExist("No round matching '%s'" % name)

    def get_queryset(self):
        return super(RoundManager, self).get_queryset().select_related('tournament').order_by('seq')


class Round(models.Model):
    DRAW_RANDOM      = 'R'
    DRAW_MANUAL      = 'M'
    DRAW_ROUNDROBIN  = 'D'
    DRAW_POWERPAIRED = 'P'
    DRAW_FIRSTBREAK  = 'F'
    DRAW_BREAK       = 'B'
    DRAW_CHOICES = (
        (DRAW_RANDOM,      'Random'),
        (DRAW_MANUAL,      'Manual'),
        (DRAW_ROUNDROBIN,  'Round-robin'),
        (DRAW_POWERPAIRED, 'Power-paired'),
        (DRAW_FIRSTBREAK,  'First elimination'),
        (DRAW_BREAK,       'Subsequent elimination'),
    )

    STAGE_PRELIMINARY = 'P'
    STAGE_ELIMINATION = 'E'
    STAGE_CHOICES = (
        (STAGE_PRELIMINARY, 'Preliminary'),
        (STAGE_ELIMINATION, 'Elimination'),
    )

    STATUS_NONE      = 'N'
    STATUS_DRAFT     = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_RELEASED  = 'R'
    STATUS_CHOICES = (
        (STATUS_NONE,      'None'),
        (STATUS_DRAFT,     'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_RELEASED,  'Released'),
    )

    objects = RoundManager()

    tournament     = models.ForeignKey(Tournament)
    seq            = models.IntegerField(help_text="A number that determines the order of the round, IE 1 for the initial round")
    name           = models.CharField(max_length=40, help_text="e.g. \"Round 1\"")
    abbreviation   = models.CharField(max_length=10, help_text="e.g. \"R1\"")
    draw_type      = models.CharField(max_length=1, choices=DRAW_CHOICES, help_text="Which draw technique to use")
    stage          = models.CharField(max_length=1, choices=STAGE_CHOICES, default=STAGE_PRELIMINARY, help_text="Preliminary = inrounds, elimination = outrounds")
    break_category = models.ForeignKey('breakqual.BreakCategory', blank=True, null=True, help_text="If elimination round, which break category")

    draw_status        = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE)
    venue_status       = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE)
    adjudicator_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE)

    checkins = models.ManyToManyField('participants.Person', through='availability.Checkin', related_name='checkedin_rounds')

    active_venues       = models.ManyToManyField('venues.Venue', through='availability.ActiveVenue')
    active_adjudicators = models.ManyToManyField('participants.Adjudicator', through='availability.ActiveAdjudicator')
    active_teams        = models.ManyToManyField('participants.Team', through='availability.ActiveTeam')

    feedback_weight = models.FloatField(default=0)
    silent = models.BooleanField(default=False)
    motions_released = models.BooleanField(default=False)
    starts_at = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = [('tournament', 'seq')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']
        verbose_name = "⏰ Round"

    def __str__(self):
        return "%s - %s" % (self.tournament, self.name)

    @property
    def rounds(self):
        from warnings import warn
        warn("Tournament.rounds is deprecated, use Tournament.round_set instead.", DeprecationWarning)
        return self.round_set

    def motions(self):
        from warnings import warn
        warn("Tournament.motions is deprecated, use Tournament.motion_set instead.", DeprecationWarning)
        return self.motion_set

    def draw(self, override_team_checkins=False):
        from draw.models import Debate, TeamPositionAllocation
        from draw import DrawGenerator
        from participants.models import Team

        if self.draw_status != self.STATUS_NONE:
            raise RuntimeError("Tried to run draw on round that already has a draw")

        # Delete all existing debates for this round.
        self.debate_set.all().delete()

        # There is a bit of logic to go through to figure out what we need to
        # provide to the draw class.
        OPTIONS_TO_CONFIG_MAPPING = {
            "avoid_institution"  : "draw_rules__avoid_same_institution",
            "avoid_history"      : "draw_rules__avoid_team_history",
            "history_penalty"    : "draw_rules__team_history_penalty",
            "institution_penalty": "draw_rules__team_institution_penalty",
            "side_allocations"   : "draw_rules__draw_side_allocations",
        }

        if override_team_checkins is True:
            draw_teams = self.tournament.team_set.all()
        else:
            draw_teams = self.active_teams.all()

        # Set type-specific options
        if self.draw_type == self.DRAW_RANDOM:
            teams = draw_teams
            draw_type = "random"
            OPTIONS_TO_CONFIG_MAPPING.update({
                "avoid_conflicts" : "draw_rules__draw_avoid_conflicts",
            })
        elif self.draw_type == self.DRAW_MANUAL:
            teams = draw_teams
            draw_type = "manual"
        elif self.draw_type == self.DRAW_POWERPAIRED:
            from standings.standings import annotate_team_standings
            teams = annotate_team_standings(draw_teams, self.prev, shuffle=True)
            draw_type = "power_paired"
            OPTIONS_TO_CONFIG_MAPPING.update({
                "avoid_conflicts" : "draw_rules__draw_avoid_conflicts",
                "odd_bracket"     : "draw_rules__draw_odd_bracket",
                "pairing_method"  : "draw_rules__draw_pairing_method",
            })
        elif self.draw_type == self.DRAW_ROUNDROBIN:
            teams = draw_teams
            draw_type = "round_robin"
        else:
            raise RuntimeError("Break rounds aren't supported yet.")

        # Annotate attributes as required by DrawGenerator.
        if self.prev:
            for team in teams:
                team.aff_count = team.get_aff_count(self.prev.seq)
        else:
            for team in teams:
                team.aff_count = 0

        # Evaluate this query set first to avoid hitting the database inside a loop.
        tpas = dict()
        TPA_MAP = {TeamPositionAllocation.POSITION_AFFIRMATIVE: "aff",
            TeamPositionAllocation.POSITION_NEGATIVE: "neg"}
        for tpa in self.teampositionallocation_set.all():
            tpas[tpa.team] = TPA_MAP[tpa.position]
        for team in teams:
            if team in tpas:
                team.allocated_side = tpas[team]
        del tpas

        options = dict()
        for key, value in OPTIONS_TO_CONFIG_MAPPING.items():
            options[key] = self.tournament.preferences[value]
        if options["side_allocations"] == "manual-ballot":
            options["side_allocations"] = "balance"

        drawer = DrawGenerator(draw_type, teams, results=None, **options)
        draw = drawer.generate()
        self.make_debates(draw)
        self.draw_status = self.STATUS_DRAFT
        self.save()

    def allocate_adjudicators(self, alloc_class=SAAllocator):
        if self.draw_status != self.STATUS_CONFIRMED:
            raise RuntimeError("Tried to allocate adjudicators on unconfirmed draw")

        debates = self.get_draw()
        adjs = list(self.active_adjudicators.accredited())
        allocator = alloc_class(debates, adjs)

        for alloc in allocator.allocate():
            alloc.save()

        self.adjudicator_status = self.STATUS_DRAFT
        self.save()

    @property
    def adjudicators_allocation_validity(self):
        debates = self.get_cached_draw
        if not all(debate.adjudicators.has_chair for debate in debates):
            return 1
        if not all(debate.adjudicators.valid for debate in debates):
            return 2
        return 0

    def venue_allocation_validity(self):
        debates = self.get_cached_draw
        if all(debate.venue for debate in debates):
            return True
        else:
            return False

    @cached_property
    def get_cached_draw(self):
        return self.get_draw()

    def get_draw(self):
        if self.tournament.pref('enable_divisions'):
            debates = self.debate_set.order_by('room_rank').select_related(
                    'venue', 'division', 'division__venue_group')
        else:
            debates = self.debate_set.order_by('room_rank').select_related(
                    'venue')

        return debates

    def get_draw_by_room(self):
        if self.tournament.pref('enable_divisions'):
            debates = self.debate_set.order_by('venue__name').select_related(
                    'venue', 'division', 'division__venue_group')
        else:
            debates = self.debate_set.order_by('venue__name').select_related(
                    'venue')

        return debates

    def get_draw_by_team(self):
        # TODO is there a more efficient way to do this?
        draw_by_team = list()
        for debate in self.debate_set.all():
            draw_by_team.append((debate.aff_team, debate))
            draw_by_team.append((debate.neg_team, debate))
        draw_by_team.sort(key=lambda x: str(x[0]))
        return draw_by_team

    def get_draw_with_standings(self, round):
        from participants.models import Team
        draw = self.get_draw()
        if round.prev:
            if round.tournament.pref('team_points_rule') != "wadl":
                standings = list(Team.objects.subrank_standings(round.prev))
                for debate in draw:
                    for side in ('aff_team', 'neg_team'):
                        # TODO is there a more efficient way to do this?
                        team = getattr(debate, side)
                        setattr(debate, side + "_cached", team)
                        annotated_team = [x for x in standings if x == team]
                        if len(annotated_team) == 1:
                            annotated_team = annotated_team[0]
                            for attr in ('points', 'speaker_score', 'subrank', 'draw_strength', 'margins', 'who_beat_whom_display'):
                                setattr(team, attr, getattr(annotated_team, attr, None))
                            if annotated_team.points:
                                team.pullup = abs(annotated_team.points - debate.bracket) >= 1 # don't highlight intermediate brackets that look within reason
            else:
                standings = list(Team.objects.standings(round.prev))

        return draw

    def make_debates(self, pairings):
        from draw.models import Debate, DebateTeam
        import random

        venues = list(self.active_venues.order_by('-priority'))[:len(pairings)]

        if len(venues) < len(pairings):
            raise DrawError("There are %d debates but only %d venues." % (len(pairings), len(venues)))

        random.shuffle(venues)
        random.shuffle(pairings) # to avoid IDs indicating room ranks

        for pairing in pairings:
            try:
                if pairing.division:
                    if (pairing.teams[0].type == "B") or (pairing.teams[1].type == "B"):
                        # If the match is a bye then they don't get a venue
                        selected_venue = None
                    else:
                        selected_venue = next(v for v in venues if v.group == pairing.division.venue_group)
                        venues.pop(venues.index(selected_venue))
                else:
                    selected_venue = venues.pop(0)
            except:
                print("Error assigning venues")
                selected_venue = None

            debate = Debate(round=self, venue=selected_venue)

            debate.division = pairing.division
            debate.bracket   = pairing.bracket
            debate.room_rank = pairing.room_rank
            debate.flags     = ",".join(pairing.flags) # comma-separated list
            debate.save()

            aff = DebateTeam(debate=debate, team=pairing.teams[0], position=DebateTeam.POSITION_AFFIRMATIVE)
            neg = DebateTeam(debate=debate, team=pairing.teams[1], position=DebateTeam.POSITION_NEGATIVE)

            aff.save()
            neg.save()

    # TODO: all these availability methods should be in the availability app

    def base_availability(self, model, active_table, active_column, model_table,
                         id_field='id'):
        d = {
            'active_table' : active_table,
            'active_column' : active_column,
            'model_table': model_table,
            'id_field': id_field,
            'id' : self.id,
        }
        return model.objects.all().extra(select={'is_active': """EXISTS (Select 1
                                                 from %(active_table)s
                                                 drav where
                                                 drav.%(active_column)s =
                                                 %(model_table)s.%(id_field)s and
                                                 drav.round_id=%(id)d)""" % d })

    def person_availability(self):
        from participants.models import Person
        return self.base_availability(Person, 'availability_checkin', 'person_id',
                                      'participants_person')


    def venue_availability(self):
        from venues.models import Venue
        all_venues = self.base_availability(Venue, 'availability_activevenue', 'venue_id',
                                      'venues_venue')
        all_venues = [v for v in all_venues if v.tournament == self.tournament]
        return all_venues

    def unused_venues(self):
        from venues.models import Venue
        # Had to replicate venue_availability via base_availability so extra()
        # could still function on the query set
        result = self.base_availability(Venue, 'availability_activevenue', 'venue_id',
                                      'venues_venue').extra(select =
                                      {'is_used': """EXISTS (SELECT 1
                                      FROM draw_debate da
                                      WHERE da.round_id=%d AND
                                      da.venue_id = venues_venue.id)""" % self.id},
        )
        return [v for v in result if v.is_active and not v.is_used and v.tournament == self.tournament]

    def adjudicator_availability(self):
        from participants.models import Adjudicator
        all_adjs = self.base_availability(Adjudicator, 'availability_activeadjudicator',
                                      'adjudicator_id',
                                      'participants_adjudicator', id_field='person_ptr_id')

        if not self.tournament.pref('share_adjs'):
            all_adjs = [a for a in all_adjs if a.tournament == self.tournament]

        return all_adjs

    def unused_adjudicators(self):
        from participants.models import Adjudicator
        result = self.base_availability(Adjudicator, 'availability_activeadjudicator',
                                      'adjudicator_id',
                                      'participants_adjudicator',
                                      id_field='person_ptr_id').extra(
                                        select = {'is_used': """EXISTS (SELECT 1
                                                  FROM adjallocation_debateadjudicator da
                                                  LEFT JOIN draw_debate d ON da.debate_id = d.id
                                                  WHERE d.round_id = %d AND
                                                  da.adjudicator_id = participants_adjudicator.person_ptr_id)""" % self.id },
        )
        if not self.tournament.pref('draw_skip_adj_checkins'):
            return [a for a in result if a.is_active and not a.is_used]
        else:
            return [a for a in result if not a.is_used]

    def team_availability(self):
        from participants.models import Team
        all_teams = self.base_availability(Team, 'availability_activeteam', 'team_id',
                                      'participants_team')
        relevant_teams = [t for t in all_teams if t.tournament == self.tournament]
        return relevant_teams

    def unused_teams(self):
        from draw.models import DebateTeam
        all_teams = self.active_teams.all()
        all_teams = [t for t in all_teams if t.tournament == self.tournament]

        debating_teams = [t.team for t in DebateTeam.objects.filter(debate__round=self).select_related('team', 'debate')]
        unused_teams = [t for t in all_teams if t not in debating_teams]

        return unused_teams

    def set_available_base(self, ids, model, active_model, get_active,
                             id_column, active_id_column, remove=True):
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

    def set_available_people(self, ids):
        from availability.models import Checkin
        from participants.models import Person
        return self.set_available_base(ids, Person, Checkin,
                                      self.checkins, 'person_id',
                                      'person__id', remove=False)

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
        return self.set_available_base(ids, Team, ActiveTeam,
                                       self.active_teams, 'team_id',
                                      'team__id')

    def activate_adjudicator(self, adj, state=True):
        from availability.models import ActiveAdjudicator
        if state:
            ActiveAdjudicator.objects.get_or_create(round=self, adjudicator=adj)
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

    def activate_all(self):
        from venues.models import Venue
        self.set_available_venues([v.id for v in Venue.objects.all()])
        self.set_available_adjudicators([a.id for a in Adjudicator.objects.all()])
        self.set_available_teams([t.id for t in Team.objects.all()])

    @property
    def prev(self):
        try:
            return Round.objects.get(seq=self.seq-1, tournament=self.tournament)
        except Round.DoesNotExist:
            return None

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()

def update_round_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s_%s" % (instance.tournament.slug, instance.seq, 'object')
    cache.delete(cached_key)
    logger.debug("Updated cache %s for %s" % (cached_key, instance))

# Update the cached round object when model is changed)
signals.post_save.connect(update_round_cache, sender=Round)



class SRManager(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(SRManager, self).get_queryset().select_related('debate')


