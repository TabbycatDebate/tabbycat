import random
import re
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned

from debate.utils import pair_list, memoize
from debate.adjudicator.anneal import SAAllocator
from debate.result import BallotSet
from debate.draw import DrawGenerator, DrawError, DRAW_FLAG_DESCRIPTIONS

from warnings import warn
from threading import BoundedSemaphore
from collections import OrderedDict


class ScoreField(models.FloatField):
    pass

class Tournament(models.Model):

    slug = models.SlugField(unique=True)
    current_round = models.ForeignKey('Round', null=True, blank=True,
                                     related_name='tournament_')
    welcome_msg = models.TextField(blank=True, null=True, default="")
    release_all = models.BooleanField(default=False)

    @models.permalink
    def get_absolute_url(self):
        return ('tournament_home', [self.slug])

    @property
    def teams(self):
        return Team.objects.filter(institution__tournament=self)

    def prelim_rounds(self, before=None, until=None):
        qs = Round.objects.filter(stage=Round.STAGE_PRELIMINARY, tournament=self)
        if until:
            qs = qs.filter(seq__lte=until.seq)
        if before:
            qs = qs.filter(seq__lt=before.seq)
        return qs

    def create_next_round(self):
        curr = self.current_round
        next = curr.seq + 1
        r = Round(name="Round %d" % next, seq=next, type=Round.DRAW_POWERPAIRED,
                  tournament=self)
        r.save()
        r.activate_all()

    @property
    def config(self):
        if not hasattr(self, '_config'):
            from debate.config import Config
            self._config = Config(self)
        return self._config

    @property
    def LAST_SUBSTANTIVE_POSITION(self):
        return 3

    @property
    def REPLY_POSITION(self):
        return 4

    @property
    def REPLIES_ENABLED(self):
        return True

    @property
    def POSITIONS(self):
        return range(1, 5)

    def __unicode__(self):
        return unicode(self.slug)

class VenueGroup(models.Model):
    name = models.CharField(max_length=40)
    tournament = models.ForeignKey(Tournament)

    def __unicode__(self):
        return u'%s' % (self.name)

class Venue(models.Model):
    name = models.CharField(max_length=40)
    group = models.ForeignKey(VenueGroup, blank=True, null=True)
    priority = models.IntegerField()
    tournament = models.ForeignKey(Tournament)

    def __unicode__(self):
        return u'%s %s (%d)' % (self.group, self.name, self.priority)

class Institution(models.Model):
    tournament = models.ForeignKey(Tournament)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=8, default="")

    class Meta:
        unique_together = [('tournament', 'code')]

    def __unicode__(self):
        return unicode(self.name)

    @property
    def short_code(self):
        if self.abbreviation:
            return self.abbreviation
        else:
            return self.code[:5]


def annotate_team_standings(teams, round=None, shuffle=False):
    """Accepts a QuerySet, returns a list.
    If 'shuffle' is True, it shuffles the list before sorting so that teams that
    are equal are in random order. This should be turned on for draw generation,
    and turned off for display."""
    # This is what might be more concisely expressed, if it were permissible
    # in Django, as:
    # teams = teams.annotate_if(
    #     dict(points = models.Count('debateteam__teamscore__points'),
    #     speaker_score = models.Count('debateteam__teamscore__score')),
    #     dict(debateteam__teamscore__ballot_submission__confirmed = True)
    # )
    # That is, it adds up all the wins and points of each team on CONFIRMED
    # ballots and adds them as columns to the table it returns.
    # The standings include only preliminary rounds.

    EXTRA_QUERY = """
        SELECT DISTINCT SUM({field:s})
        FROM "debate_teamscore"
        JOIN "debate_ballotsubmission" ON "debate_teamscore"."ballot_submission_id" = "debate_ballotsubmission"."id"
        JOIN "debate_debateteam" ON "debate_teamscore"."debate_team_id" = "debate_debateteam"."id"
        JOIN "debate_debate" ON "debate_debateteam"."debate_id" = "debate_debate"."id"
        JOIN "debate_round" ON "debate_debate"."round_id" = "debate_round"."id"
        WHERE "debate_ballotsubmission"."confirmed" = True
        AND "debate_debateteam"."team_id" = "debate_team"."id"
        AND "debate_round"."stage" = '""" + str(Round.STAGE_PRELIMINARY) + "\'"

    if round is not None:
        EXTRA_QUERY += """AND "debate_round"."seq" <= {round:d}""".format(round=round.seq)

    teams = teams.extra({
        "points": EXTRA_QUERY.format(field="points"),
        "speaker_score": EXTRA_QUERY.format(field="score"),
    }).distinct()

    # Extract which rule to use from the tournament config
    if round is not None:
        tournament = round.tournament
    else:
        tournament = teams[0].institution.tournament
    rule = tournament.config.get('team_standings_rule')

    if rule == "australs":

        if shuffle:
            sorted_teams = list(teams)
            random.shuffle(sorted_teams) # shuffle first, so that if teams are truly equal, they'll be in random order
            sorted_teams.sort(key=lambda x: (x.points, x.speaker_score), reverse=True)
            return sorted_teams
        else:
            teams = teams.order_by("-points", "-speaker_score")
            return list(teams)

    elif rule == "nz":

        # Add draw strength annotation.
        for team in teams:
            draw_strength = 0
            # Find all teams that they've faced.
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            for dt in debateteam_set:
                # Can't just use dt.opposition.team.points, as dt.opposition.team isn't annotated.
                draw_strength += teams.get(id=dt.opposition.team.id).points
            team.draw_strength = draw_strength

        def who_beat_whom(team1, team2):
            """Returns a positive value if team1 won more debates, a negative value
            if team2 won more, 0 if the teams won the same number against each other
            or haven't faced each other."""
            # Find all debates between these two teams
            def get_wins(team, other):
                ts =  TeamScore.objects.filter(
                    ballot_submission__confirmed=True,
                    debate_team__team=team,
                    debate_team__debate__debateteam__team=other).aggregate(models.Sum('points'))
                return ts["points__sum"]
            wins1 = get_wins(team1, team2)
            wins2 = get_wins(team2, team1)
            # Print this to the logs, just so we know it happened
            print "who beat whom, {0} vs {1}: {2} wins against {3}".format(team1, team2, wins1, wins2)
            return cmp(wins1, wins2)

        def cmp_teams(team1, team2):
            """Returns 1 if team1 ranks ahead of team2, -1 if team2 ranks ahead of team1,
            and 0 if they rank the same. Requires access to teams, so that it knows whether
            it can apply who-beat-whom."""
            # If there are only two teams on this number of points, or points/speakers,
            # or points/speaks/draw-strength, then use who-beat-whom.
            def two_teams_left(key):
                return key(team1) == key(team2) and len(filter(lambda x: key(x) == key(team1), teams)) == 2
            if two_teams_left(lambda x: x.points) or two_teams_left(lambda x: (x.points, x.speaker_score)) \
                    or two_teams_left(lambda x: (x.points, x.speaker_score, x.draw_strength)):
                winner = who_beat_whom(team1, team2)
                if winner != 0: # if this doesn't help, keep going
                    return winner
            key = lambda x: (x.points, x.speaker_score, x.draw_strength)
            return cmp(key(team1), key(team2))

        sorted_teams = list(teams)
        if shuffle:
            random.shuffle(sorted_teams) # shuffle first, so that if teams are truly equal, they'll be in random order
        sorted_teams.sort(cmp=cmp_teams, reverse=True)
        return sorted_teams

    else:
        raise ValueError("Invalid team_standings_rule option: {0}".format(rule))


class TeamManager(models.Manager):
    def standings(self, round):
        """Returns a list."""
        teams = self.filter(
            institution__tournament=round.tournament,
            debateteam__debate__round__seq__lte = round.seq,
        )
        return annotate_team_standings(teams, round)

    def ranked_standings(self, round):
        """Returns a list."""

        teams = self.standings(round)

        prev_rank_value = (None, None)
        current_rank = 0
        for i, team in enumerate(teams, start=1):
            rank_value = (team.points, team.speaker_score)
            if rank_value != prev_rank_value:
                current_rank = i
                prev_rank_value = rank_value
            team.rank = current_rank

        return teams

    def subrank_standings(self, round):
        """Returns a list."""
        teams = self.standings(round)

        prev_rank_value = None
        prev_points = None
        current_rank = 0
        for team in teams:
            if team.points != prev_points:
                counter = 1
                prev_points = team.points
            rank_value = team.speaker_score
            if rank_value != prev_rank_value:
                current_rank = counter
                prev_rank_value = rank_value
            team.subrank = current_rank
            counter += 1

        return teams

    def breaking_teams(self, tournament, category='open'):
        """Returns a list."""

        FILTER_ARGS = {
            'open': dict(),
            'esl':  dict(type=Team.TYPE_ESL),
        }
        filterargs = FILTER_ARGS[category]

        teams = self.filter(institution__tournament=tournament, **filterargs)
        teams = annotate_team_standings(teams)

        BREAK_SIZE_CONFIG_OPTIONS = {
            'open': 'break_size',
            'esl':  'esl_break_size',
        }
        break_size = tournament.config.get(BREAK_SIZE_CONFIG_OPTIONS[category])
        institution_cap = tournament.config.get('institution_cap')

        prev_rank_value = (None, None)
        current_rank = 0
        breaking_teams = list()

        # If there's an institution cap, variables for it:
        if institution_cap > 0:
            current_break_rank = 0
            current_break_seq = 0
            from collections import Counter
            teams_from_institution = Counter()

        for i, team in enumerate(teams, start=1):

            # Overall rank
            rank_value = (team.points, team.speaker_score)
            new_rank = rank_value != prev_rank_value
            if new_rank:
                current_rank = i
                prev_rank_value = rank_value
            team.rank = current_rank

            if institution_cap > 0:
                # Increment current_break_seq if it won't violate institution cap
                if teams_from_institution[team.institution] >= institution_cap:
                    if new_rank and current_break_rank == break_size:
                        break
                    team.break_rank = None

                else:
                    current_break_seq += 1
                    if new_rank:
                        if current_break_rank == break_size:
                            break
                        current_break_rank = current_break_seq
                    team.break_rank = current_break_rank
                # Take note of the institution
                teams_from_institution[team.institution] += 1
            else:
                if current_rank > break_size:
                    break

            breaking_teams.append(team)

        return breaking_teams


class Team(models.Model):
    reference = models.CharField(max_length=50, verbose_name="Name or suffix")
    institution = models.ForeignKey(Institution)
    use_institution_prefix = models.BooleanField(default=True, verbose_name="Name uses institutional prefix then suffix")

    # set to True if a team is ineligible to break (other than being
    # swing/composite)
    cannot_break = models.BooleanField(default=False)

    # Records the list of venues a team is willing to debate in
    venue_group_preferences = models.ManyToManyField(VenueGroup, blank=True, verbose_name='For when a team can only debate in specific venues')

    TYPE_NONE = 'N'
    TYPE_ESL = 'E'
    TYPE_SWING = 'S'
    TYPE_COMPOSITE = 'C'
    TYPE_CHOICES = (
        (TYPE_NONE, 'None'),
        (TYPE_ESL, 'ESL'),
        (TYPE_SWING, 'Swing'),
        (TYPE_COMPOSITE, 'Composite'),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                            default=TYPE_NONE)

    class Meta:
        unique_together = [('reference', 'institution')]

    objects = TeamManager()

    def __unicode__(self):
        return self.short_name

    @property
    def name(self):
        # TODO make this an exception so that we get rid of all of them
        warn("Team.name is deprecated, use Team.short_name", DeprecationWarning, stacklevel=2)
        return self.short_name

    @property
    def short_name(self):
        if self.use_institution_prefix:
            return unicode(self.institution.code + " " + self.reference)
        else:
            return unicode(self.reference)

    @property
    def long_name(self):
        if self.use_institution_prefix:
            return unicode(self.institution.name + " " + self.reference)
        else:
            return unicode(self.reference)

    def get_aff_count(self, seq=None):
        return self._get_count(DebateTeam.POSITION_AFFIRMATIVE, seq)

    def get_neg_count(self, seq=None):
        return self._get_count(DebateTeam.POSITION_NEGATIVE, seq)

    def _get_count(self, position, seq):
        dts = DebateTeam.objects.filter(team=self, position=position, debate__round__stage=Round.STAGE_PRELIMINARY)
        if seq is not None:
            dts = dts.filter(debate__round__seq__lte=seq)
        return dts.count()

    def get_debates(self, before_round):
        dts = DebateTeam.objects.select_related('debate').filter(team=self).order_by('debate__round__seq')
        if before_round is not None:
            dts = dts.filter(debate__round__seq__lt=before_round)
        return [dt.debate for dt in dts]

    @property
    def debates(self):
        return self.get_debates(None)

    def seen(self, other, before_round=None):
        debates = self.get_debates(before_round)
        return len([1 for d in debates if other in d])

    def same_institution(self, other):
        return self.institution_id == other.institution_id

    def prev_debate(self, round_seq):
        try:
            return DebateTeam.objects.filter(
                debate__round__seq__lt=round_seq,
                team=self,
            ).order_by('-debate__round__seq')[0].debate
        except IndexError:
            return None

    @property
    def speakers(self):
        return self.speaker_set.all()

class SpeakerManager(models.Manager):
    def standings(self, round=None):
        # only include scoresheets for up to this round, exclude replies
        if round:
            speakers = self.filter(
                team__institution__tournament=round.tournament,
                speakerscore__position__lte=round.tournament.LAST_SUBSTANTIVE_POSITION,
                speakerscore__debate_team__debate__round__seq__lte = round.seq,
            )
        else:
            speakers = self.filter(
                team__institution__tournament=round.tournament,
                speakerscore__position__lte=round.tournament.LAST_SUBSTANTIVE_POSITION,
            )

        # TODO is there a way to add round scores without so many database hits?
        # Maybe using a select subquery?

        # This is what might be more concisely expressed, if it were permissible
        # in Django, as:
        # speakers = speakers.annotate_if(
        #     dict(total = models.Sum('speakerscore__score')),
        #     dict(ballot_submission__confirmed = True)
        # )
        # That is, it adds up all the points of each speaker on CONFIRMED
        # ballots and adds them as columns to the table it returns.
        EXTRA_QUERY = """
            SELECT DISTINCT {aggregator:s}("score")
            FROM "debate_speakerscore"
            JOIN "debate_debateteam" ON "debate_speakerscore"."debate_team_id" = "debate_debateteam"."id"
            JOIN "debate_debate" ON "debate_debateteam"."debate_id" = "debate_debate"."id"
            JOIN "debate_round" ON "debate_debate"."round_id" = "debate_round"."id"
            JOIN "debate_ballotsubmission" ON "debate_speakerscore"."ballot_submission_id" = "debate_ballotsubmission"."id"
            WHERE "debate_ballotsubmission"."confirmed" = True
            AND "debate_speakerscore"."speaker_id" = "debate_speaker"."person_ptr_id"
            AND "debate_speakerscore"."position" <= {position:d}
            AND "debate_round"."seq" <= {round:d}
            AND "debate_round"."stage" = '{stage}'
        """
        speakers = speakers.extra({"total": EXTRA_QUERY.format(
            aggregator = "SUM",
            round = round.seq,
            position = round.tournament.LAST_SUBSTANTIVE_POSITION,
            stage = round.STAGE_PRELIMINARY,
        ), "average": EXTRA_QUERY.format(
            aggregator = "AVG",
            round = round.seq,
            position = round.tournament.LAST_SUBSTANTIVE_POSITION,
            stage = round.STAGE_PRELIMINARY,
        )}).distinct().order_by('-total')

        prev_total = None
        current_rank = 0
        for i, speaker in enumerate(speakers, start=1):
            if speaker.total != prev_total:
                current_rank = i
                prev_total = speaker.total
            speaker.rank = current_rank

        return speakers

    def reply_standings(self, round=None):
        # If replies aren't enabled, return an empty queryset.
        if not round.tournament.REPLIES_ENABLED:
            return self.objects.none()

        if round:
            speakers = self.filter(
                team__institution__tournament=round.tournament,
                speakerscore__position=round.tournament.REPLY_POSITION,
                speakerscore__debate_team__debate__round__seq__lte =
                round.seq,
            )
        else:
            speakers = self.filter(
                team__institution__tournament=round.tournament,
                speakerscore__position=round.tournament.REPLY_POSITION,
            )

        # This is what might be more concisely expressed, if it were permissible
        # in Django, as:
        # speakers = speakers.annotate_if(
        #     dict(average = models.Avg('speakerscore__score'),
        #          count   = models.Count('speakerscore__score')),
        #     dict(ballot_submission__confirmed = True)
        # )
        # That is, it adds up all the reply scores of each speaker on CONFIRMED
        # ballots and adds them as columns to the table it returns.
        EXTRA_QUERY = """
            SELECT DISTINCT {aggregator:s}("score")
            FROM "debate_speakerscore"
            JOIN "debate_debateteam" ON "debate_speakerscore"."debate_team_id" = "debate_debateteam"."id"
            JOIN "debate_debate" ON "debate_debateteam"."debate_id" = "debate_debate"."id"
            JOIN "debate_round" ON "debate_debate"."round_id" = "debate_round"."id"
            JOIN "debate_ballotsubmission" ON "debate_speakerscore"."ballot_submission_id" = "debate_ballotsubmission"."id"
            WHERE "debate_ballotsubmission"."confirmed" = True
            AND "debate_speakerscore"."speaker_id" = "debate_speaker"."person_ptr_id"
            AND "debate_speakerscore"."position" = {position:d}
            AND "debate_round"."seq" <= {round:d}
            AND "debate_round"."stage" = '{stage}'
        """
        speakers = speakers.extra({"average": EXTRA_QUERY.format(
            aggregator = "AVG",
            round = round.seq,
            position = round.tournament.REPLY_POSITION,
            stage = round.STAGE_PRELIMINARY
        ), "replies": EXTRA_QUERY.format(
            aggregator = "COUNT",
            round = round.seq,
            position = round.tournament.REPLY_POSITION,
            stage = round.STAGE_PRELIMINARY
        )}).distinct().order_by('-average', '-replies', 'name')

        # Use this to filter out speakers with an unconfirmed ballot submission,
        # since they get caught up in the query above.
        speakers_filtered = filter(lambda x: x.replies > 0, speakers)

        prev_rank_value = (None, None)
        current_rank = 0
        for i, speaker in enumerate(speakers_filtered, start=1):
            rank_value = (speaker.average, speaker.replies)
            if rank_value != prev_rank_value:
                current_rank = i
                prev_rank_value = rank_value
            speaker.rank = current_rank

        return speakers_filtered


class Person(models.Model):
    name = models.CharField(max_length=40)
    barcode_id = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)

    checkin_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    @property
    def has_contact(self):
        return bool(self.email or self.phone)


class Checkin(models.Model):
    person = models.ForeignKey('Person')
    round = models.ForeignKey('Round')


class Speaker(Person):
    team = models.ForeignKey(Team)

    objects = SpeakerManager()

    def __unicode__(self):
        return unicode(self.name)


class AdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def accredited(self):
        return self.filter(is_trainee=False)


class Adjudicator(Person):
    institution = models.ForeignKey(Institution)
    test_score = models.FloatField(default=0)

    institution_conflicts = models.ManyToManyField('Institution', through='AdjudicatorInstitutionConflict', related_name='adjudicator_institution_conflicts')
    conflicts = models.ManyToManyField('Team', through='AdjudicatorConflict')

    is_trainee = models.BooleanField(default=False)
    breaking = models.BooleanField(default=False)

    objects = AdjudicatorManager()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)

    def conflict_with(self, team):
        if not hasattr(self, '_conflict_cache'):
            self._conflict_cache = set(c['team_id'] for c in
                AdjudicatorConflict.objects.filter(adjudicator=self).values('team_id')
            )
            self._institution_conflict_cache = set(c['institution_id'] for c in
                AdjudicatorInstitutionConflict.objects.filter(adjudicator=self).values('institution_id')
            )
        return team.id in self._conflict_cache or team.institution_id in self._institution_conflict_cache

    @property
    def tournament(self):
        return self.institution.tournament

    @property
    def score(self):
        weight = self.tournament.current_round.feedback_weight

        feedback_score = self._feedback_score()
        if feedback_score is None:
            feedback_score = 0
            weight = 0

        return self.test_score * (1 - weight) + (weight * feedback_score)


    @property
    def rscores(self):
        r = []
        for round in self.institution.tournament.rounds.all():
            q = models.Q(source_adjudicator__debate__round=round) | \
                    models.Q(source_team__debate__round=round)
            a = AdjudicatorFeedback.objects.filter(
                adjudicator = self,
                confirmed = True
            ).filter(q).aggregate(avg=models.Avg('score'))['avg']
            r.append(a)
        return r

    def _feedback_score(self):
        return AdjudicatorFeedback.objects.filter(
            adjudicator = self,
            confirmed = True
        ).aggregate(avg=models.Avg('score'))['avg']

    @property
    def feedback_score(self):
        return self._feedback_score() or 0


    def get_feedback(self):
        return AdjudicatorFeedback.objects.filter(adjudicator=self)

    def seen_team(self, team, before_round=None):
        if not hasattr(self, '_seen_cache'):
            self._seen_cache = {}
        if before_round not in self._seen_cache:
            qs = DebateTeam.objects.filter(
                debate__debateadjudicator__adjudicator=self
            )
            if before_round is not None:
                qs = qs.filter(
                    debate__round__seq__lt = before_round.seq
                )
            self._seen_cache[before_round] = set(dt.team.id for dt in qs)
        return team.id in self._seen_cache[before_round]

    def seen_adjudicator(self, adj, before_round=None):
        d = DebateAdjudicator.objects.filter(
            adjudicator = self,
            debate__debateadjudicator__adjudicator = adj,
        )
        if before_round is not None:
            d = d.filter(
                debate__round__seq__lt = before_round.seq
            )
        return d.count()


class AdjudicatorTestScoreHistory(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    round = models.ForeignKey('Round', blank=True, null=True)
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Adjudicator test score histories"


class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    team = models.ForeignKey(Team)


class AdjudicatorInstitutionConflict(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    institution = models.ForeignKey(Institution)


class RoundManager(models.Manager):
    use_for_related_Fields = True

    def get_queryset(self):
        return super(RoundManager,
                     self).get_queryset().select_related('tournament').order_by('seq')


class Round(models.Model):
    DRAW_RANDOM      = 'R'
    DRAW_POWERPAIRED = 'P'
    DRAW_FIRSTBREAK  = 'F'
    DRAW_BREAK       = 'B'
    DRAW_CHOICES = (
        (DRAW_RANDOM,      'Random'),
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

    STATUS_NONE      = 0
    STATUS_DRAFT     = 1
    STATUS_CONFIRMED = 10
    STATUS_RELEASED  = 99
    STATUS_CHOICES = (
        (STATUS_NONE,      'None'),
        (STATUS_DRAFT,     'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_RELEASED,  'Released'),
    )

    objects = RoundManager()

    tournament   = models.ForeignKey(Tournament, related_name='rounds')
    seq          = models.IntegerField()
    name         = models.CharField(max_length=40)
    abbreviation = models.CharField(max_length=10)
    draw_type    = models.CharField(max_length=1, choices=DRAW_CHOICES)
    stage        = models.CharField(max_length=1, choices=STAGE_CHOICES, default=STAGE_PRELIMINARY)

    draw_status        = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NONE)
    venue_status       = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NONE)
    adjudicator_status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NONE)

    checkins = models.ManyToManyField('Person', through='Checkin', related_name='checkedin_rounds')

    active_venues       = models.ManyToManyField('Venue', through='ActiveVenue')
    active_adjudicators = models.ManyToManyField('Adjudicator', through='ActiveAdjudicator')
    active_teams        = models.ManyToManyField('Team', through='ActiveTeam')

    feedback_weight = models.FloatField(default=0)
    silent = models.BooleanField(default=False)
    motions_released = models.BooleanField(default=False)
    starts_at = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = [('tournament', 'seq')]

    def __unicode__(self):
        return unicode(self.name)

    def motions(self):
        return self.motion_set.order_by('seq')

    def draw(self):
        if self.draw_status != self.STATUS_NONE:
            raise RuntimeError("Tried to run draw on round that already has a draw")

        # Delete all existing debates for this round.
        Debate.objects.filter(round=self).delete()

        # There is a bit of logic to go through to figure out what we need to
        # provide to the draw class.
        OPTIONS_TO_CONFIG_MAPPING = {
            "avoid_institution"  : "avoid_same_institution",
            "avoid_history"      : "avoid_team_history",
            "history_penalty"    : "team_history_penalty",
            "institution_penalty": "team_institution_penalty",
            "side_allocations"   : "draw_side_allocations",
        }

        # Set type-specific options
        if self.draw_type == self.DRAW_RANDOM:
            teams = self.active_teams.all()
            draw_type = "random"
            OPTIONS_TO_CONFIG_MAPPING.update({
                "avoid_conflicts" : "draw_avoid_conflicts",
            })
        elif self.draw_type == self.DRAW_POWERPAIRED:
            teams = annotate_team_standings(self.active_teams, self.prev, shuffle=True)
            draw_type = "power_paired"
            OPTIONS_TO_CONFIG_MAPPING.update({
                "avoid_conflicts" : "draw_avoid_conflicts",
                "odd_bracket"     : "draw_odd_bracket",
                "pairing_method"  : "draw_pairing_method",
            })
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
        for key, value in OPTIONS_TO_CONFIG_MAPPING.iteritems():
            options[key] = self.tournament.config.get(value)

        drawer = DrawGenerator(draw_type, teams, results=None, **options)
        draw = drawer.make_draw()
        self.make_debates(draw)
        self.draw_status = self.STATUS_DRAFT
        self.save()

        #from debate.draw import assign_importance
        #assign_importance(self)

    def allocate_adjudicators(self, alloc_class=SAAllocator):
        if self.draw_status != self.STATUS_CONFIRMED:
            raise RuntimeError("Tried to allocate adjudicators on unconfirmed draw")

        debates = self.get_draw()
        adjs = list(self.active_adjudicators.accredited().filter(test_score__gt=0))
        allocator = alloc_class(debates, adjs)

        for alloc in allocator.allocate():
            alloc.save()
        self.adjudicator_status = self.STATUS_DRAFT
        self.save()

    @property
    def adjudicators_allocation_validity(self):
        debates = self.get_draw()
        if not all(debate.adjudicators.has_chair for debate in debates):
            return 1
        if not all(debate.adjudicators.valid for debate in debates):
            return 2
        return 0

    def get_draw(self):
        # -bracket is included for ateneo data, which doesn't have room_rank
        return self.debate_set.order_by('room_rank', '-bracket')

    def get_draw_by_room(self):
        return self.debate_set.order_by('venue__name')

    def get_draw_by_team(self):
        # TODO is there a more efficient way to do this?
        draw_by_team = list()
        for debate in self.debate_set.all():
            draw_by_team.append((debate.aff_team, debate))
            draw_by_team.append((debate.neg_team, debate))
        draw_by_team.sort(key=lambda x: str(x[0]))
        return draw_by_team

    def get_draw_with_standings(self, round):
        draw = self.get_draw()
        if round.prev:
            standings = list(Team.objects.subrank_standings(round.prev))
            for debate in draw:
                for side in ('aff_team', 'neg_team'):
                    # TODO is there a more efficient way to do this?
                    team = getattr(debate, side)
                    annotated_team = filter(lambda x: x == team, standings)
                    if len(annotated_team) == 1:
                        annotated_team = annotated_team[0]
                        team.points = annotated_team.points
                        team.speaker_score = annotated_team.speaker_score
                        team.subrank = annotated_team.subrank
                        team.pullup = abs(annotated_team.points - debate.bracket) >= 1 # don't highlight intermediate brackets that look within reason
                        team.draw_strength = annotated_team.draw_strength
        return draw

    def make_debates(self, pairings):

        import random
        venues = list(self.active_venues.order_by('-priority'))[:len(pairings)]

        if len(venues) < len(pairings):
            raise DrawError("There are %d debates but only %d venues." % (len(pairings), len(venues)))

        random.shuffle(venues)
        random.shuffle(pairings) # to avoid IDs indicating room raks

        for pairing in pairings:
            debate = Debate(round=self, venue=venues.pop(0))
            debate.bracket   = pairing.bracket
            debate.room_rank = pairing.room_rank
            debate.flags     = ",".join(pairing.flags) # comma-separated list
            debate.save()

            aff = DebateTeam(debate=debate, team=pairing.teams[0], position=DebateTeam.POSITION_AFFIRMATIVE)
            neg = DebateTeam(debate=debate, team=pairing.teams[1], position=DebateTeam.POSITION_NEGATIVE)

            aff.save()
            neg.save()

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
        return self.base_availability(Person, 'debate_checkin', 'person_id',
                                      'debate_person')



    def venue_availability(self):
        return self.base_availability(Venue, 'debate_activevenue', 'venue_id',
                                      'debate_venue')
    def unused_venues(self):
        result = self.venue_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1
                      FROM debate_debate da
                      WHERE da.round_id=%d AND
                      da.venue_id = debate_venue.id)""" % self.id},
        )
        # if we wanted to do this with sql we'd need to use a subselect, this is much
        # easier
        return [v for v in result if v.is_active and not v.is_used]

    def adjudicator_availability(self):
        return self.base_availability(Adjudicator, 'debate_activeadjudicator',
                                      'adjudicator_id',
                                      'debate_adjudicator', id_field='person_ptr_id')

    def unused_adjudicators(self):
        result =  self.adjudicator_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1
                      FROM debate_debateadjudicator da
                      LEFT JOIN debate_debate d ON da.debate_id = d.id
                      WHERE d.round_id = %d AND
                      da.adjudicator_id = debate_adjudicator.person_ptr_id)""" % self.id },
        )
        return [a for a in result if a.is_active and not a.is_used]

    def team_availability(self):
        return self.base_availability(Team, 'debate_activeteam', 'team_id',
                                      'debate_team')

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
        return self.set_available_base(ids, Person, Checkin,
                                      self.checkins, 'person_id',
                                      'person__id', remove=False)

    def set_available_venues(self, ids):
        return self.set_available_base(ids, Venue, ActiveVenue,
                                       self.active_venues, 'venue_id',
                                       'venue__id')

    def set_available_adjudicators(self, ids):
        return self.set_available_base(ids, Adjudicator, ActiveAdjudicator,
                                       self.active_adjudicators,
                                       'adjudicator_id', 'adjudicator__id')

    def set_available_teams(self, ids):
        return self.set_available_base(ids, Team, ActiveTeam,
                                       self.active_teams, 'team_id',
                                      'team__id')

    def activate_adjudicator(self, adj, state=True):
        if state:
            ActiveAdjudicator.objects.get_or_create(round=self, adjudicator=adj)
        else:
            ActiveAdjudicator.objects.filter(round=self,
                                             adjudicator=adj).delete()

    def activate_venue(self, venue, state=True):
        if state:
            ActiveVenue.objects.get_or_create(round=self, venue=venue)
        else:
            ActiveVenue.objects.filter(round=self, venue=venue).delete()

    def activate_team(self, team, state=True):
        if state:
            ActiveTeam.objects.get_or_create(round=self, team=team)
        else:
            ActiveTeam.objects.filter(round=self, team=team).delete()

    def activate_all(self):
        self.set_available_venues([v.id for v in Venue.objects.all()])
        self.set_available_adjudicators([a.id for a in
                                         Adjudicator.objects.all()])
        self.set_available_teams([t.id for t in Team.objects.all()])

    @property
    @memoize
    def prev(self):
        try:
            return Round.objects.get(seq=self.seq-1)
        except Round.DoesNotExist:
            return None

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()


class ActiveVenue(models.Model):
    venue = models.ForeignKey(Venue)
    round = models.ForeignKey(Round)

    class Meta:
        unique_together = [('venue', 'round')]


class ActiveTeam(models.Model):
    team = models.ForeignKey(Team)
    round = models.ForeignKey(Round)

    class Meta:
        unique_together = [('team', 'round')]


class ActiveAdjudicator(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    round = models.ForeignKey(Round)

    class Meta:
        unique_together = [('adjudicator', 'round')]


class DebateManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(DebateManager, self).get_queryset().select_related(
        'round', 'venue')


class Debate(models.Model):
    STATUS_NONE      = 'N'
    STATUS_DRAFT     = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_CHOICES = (
        (STATUS_NONE,      'None'),
        (STATUS_DRAFT,     'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
    )

    objects = DebateManager()

    round = models.ForeignKey(Round)
    venue = models.ForeignKey(Venue, blank=True, null=True)

    bracket = models.FloatField(default=0)
    room_rank = models.IntegerField(default=0)

    # comma-separated list of strings
    flags = models.CharField(max_length=100, blank=True, null=True)

    importance = models.IntegerField(default=2)
    result_status = models.CharField(max_length=1, choices=STATUS_CHOICES,
            default=STATUS_NONE)
    ballot_in = models.BooleanField(default=False)

    def _get_teams(self):
        if not hasattr(self, '_team_cache'):
            self._team_cache = {}

            for t in DebateTeam.objects.filter(debate=self):
                self._team_cache[t.position] = t

    @property
    def confirmed_ballot(self):
        """Returns the confirmed ballot for this debate, or None if there is
        no such ballot."""
        try:
            return self.ballotsubmission_set.get(confirmed=True)
        except ObjectDoesNotExist: # BallotSubmission isn't defined yet, so can't use BallotSubmission.DoesNotExist
            return None

    @property
    def ballotsubmission_set_by_version(self):
        return self.ballotsubmission_set.all().order_by('version')

    @property
    def ballotsubmission_set_by_version_except_discarded(self):
        return self.ballotsubmission_set.filter(discarded=False).order_by('version')

    @property
    def identical_ballots_dict(self):
        """Returns a dict, keys are BallotSubmissions,
        values are lists of version numbers of BallotSubmissions that are
        identical to the key's BallotSubmission. Excludes discarded
        ballots (always)."""
        ballots = self.ballotsubmission_set_by_version_except_discarded
        result = dict((b, list()) for b in ballots)
        for ballot1 in ballots:
            # Save a bit of time by avoiding comparisons already done.
            # This relies on ballots being ordered by version.
            for ballot2 in ballots.filter(version__gt=ballot1.version):
                if ballot1.is_identical(ballot2):
                    result[ballot1].append(ballot2.version)
                    result[ballot2].append(ballot1.version)
        for l in result.itervalues():
            l.sort()
        return result

    @property
    def aff_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE].team

    @property
    def neg_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE].team

    def get_team(self, side):
        return getattr(self, '%s_team' % side)

    def get_dt(self, side):
        """dt = DebateTeam"""
        return getattr(self, '%s_dt' % side)

    @property
    def aff_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE]

    @property
    def neg_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE]

    @property
    def draw_conflicts(self):
        d = []
        history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
        if history:
            d.append("History conflict (%d)" % history)
        if self.aff_team.institution == self.neg_team.institution:
            d.append("Institution conflict")

        return d

    @property
    def flags_all(self):
        if not self.flags:
            return []
        else:
            return [DRAW_FLAG_DESCRIPTIONS[f] for f in self.flags.split(",")]

    @property
    def all_conflicts(self):
        return self.draw_conflicts + self.adjudicator_conflicts

    @property
    def adjudicator_conflicts(self):
        class Conflict(object):
            def __init__(self, adj, team):
                self.adj = adj
                self.team = team
            def __unicode__(self):
                return u'Adj %s + %s' % (self.adj, self.team)

        a = []
        for t, adj in self.adjudicators:
            for team in (self.aff_team, self.neg_team):
                if adj.conflict_with(team):
                    a.append(Conflict(adj, team))
        return a

    @property
    def adjudicators(self):
        adjs = DebateAdjudicator.objects.filter(debate=self)
        alloc = AdjudicatorAllocation(self)
        for a in adjs:
            if a.type == a.TYPE_CHAIR:
                alloc.chair = a.adjudicator
            if a.type == a.TYPE_PANEL:
                alloc.panel.append(a.adjudicator)
            if a.type == a.TYPE_TRAINEE:
                alloc.trainees.append(a.adjudicator)
        return alloc

    @property
    def venue_splitname(self):
        # Formatting venue names so they can split over multiple lines
        # TODO: integrate venue group name into here
        match = re.match(r"([a-z]+)([0-9]+)", str(self.venue.name), re.I)
        if match:
            items = match.groups()
            if len(items[1]) > 3:
                alloc = u'%s %s %s' % (items[0], items[1][:3], items[1][3:])
            else:
                alloc = u'%s %s' % (items[0], items[1])
        else:
            alloc = self.venue.name

        return alloc


    @property
    def result(self):
        warn("Debate.result is deprecated. Use Debate.confirmed_ballot.ballot_set instead.", DeprecationWarning, stacklevel=2)
        raise NotImplementedError("Debate.result is deprecated. Use Debate.confirmed_ballot.ballot_set instead.")

    def get_side(self, team):
        if self.aff_team == team:
            return 'aff'
        if self.neg_team == team:
            return 'neg'
        return None

    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team)

    def __unicode__(self):
        return u'[%s] %s vs %s (%s)' % (self.round.seq, self.aff_team, self.neg_team,
                                   self.venue)

    @property
    def matchup(self):
        return u'%s vs %s' % (self.aff_team.short_name, self.neg_team.short_name)


class SRManager(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(SRManager, self).get_queryset().select_related('debate', 'team', 'position')


class DebateTeam(models.Model):
    POSITION_AFFIRMATIVE = 'A'
    POSITION_NEGATIVE = 'N'
    POSITION_CHOICES = (
        (POSITION_AFFIRMATIVE, 'Affirmative'),
        (POSITION_NEGATIVE, 'Negative'),
    )

    objects = SRManager()

    debate = models.ForeignKey(Debate)
    team = models.ForeignKey(Team)

    # South can't (easily) handle custom fields, so we'll just duplicate this
    # in class TeamPositionAllocation.
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    def __unicode__(self):
        return u'%s %s' % (self.debate, self.team)

    @property
    def opposition(self):
        try:
            return DebateTeam.objects.exclude(position=self.position).get(debate=self.debate)
        except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
            print "error: ", self.debate, self.position
            return None


class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR,   'chair'),
        (TYPE_PANEL,   'panellist'),
        (TYPE_TRAINEE, 'trainee'),
    )

    objects = SRManager()

    debate = models.ForeignKey(Debate)
    adjudicator = models.ForeignKey(Adjudicator)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)

    def __unicode__(self):
        return u'%s %s' % (self.adjudicator, self.debate)


class TeamPositionAllocation(models.Model):
    """Model to store team position allocations for tournaments like Joynt Scroll
    (New Zealand). Each team-round combination should have one of these.
    In tournaments without team position allocations, just don't use this model."""

    POSITION_AFFIRMATIVE = DebateTeam.POSITION_AFFIRMATIVE
    POSITION_NEGATIVE = DebateTeam.POSITION_NEGATIVE
    POSITION_CHOICES = DebateTeam.POSITION_CHOICES

    round = models.ForeignKey(Round)
    team = models.ForeignKey(Team)
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    class Meta:
        unique_together = [('round', 'team')]


class Submission(models.Model):
    """Abstract base class to provide functionality common to different
    types of submissions.

    The unique_together class attribute of the Meta class MUST be set in
    all subclasses."""

    SUBMITTER_TABROOM = 0
    SUBMITTER_PUBLIC  = 1
    SUBMITTER_TYPE_CHOICES = (
        (SUBMITTER_TABROOM, 'Tab room'),
        (SUBMITTER_PUBLIC,  'Public'),
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()
    submitter_type = models.IntegerField(choices=SUBMITTER_TYPE_CHOICES)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True) # only relevant if submitter was in tab room
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    version_semaphore = BoundedSemaphore(100)

    confirmed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @property
    def _unique_filter_args(self):
        return dict((arg, getattr(self, arg)) for arg in self._meta.unique_together[0] if arg != 'version')

    def save(self, *args, **kwargs):
        # Check for uniqueness.
        if self.confirmed:
            try:
                current = self.__class__.objects.get(confirmed=True, **self._unique_filter_args)
            except self.DoesNotExist:
                pass
            else:
                if current != self:
                    warn("%s confirmed while %s was already confirmed, setting latter to unconfirmed" % (self, current))
                    current.confirmed = False
                    current.save()

        # Assign the version field to one more than the current maximum version.
        # Use a semaphore to protect against the possibility that two submissions do this
        # at the same time and get the same version number.
        self.version_semaphore.acquire()
        if self.pk is None:
            existing = self.__class__.objects.filter(**self._unique_filter_args)
            if existing.exists():
                self.version = existing.aggregate(models.Max('version'))['version__max'] + 1
            else:
                self.version = 1
        super(Submission, self).save(*args, **kwargs)
        self.version_semaphore.release()

    def clean(self):
        if self.submitter_type == self.SUBMITTER_TABROOM and self.user is None:
            raise ValidationError("A tab room ballot must have a user associated.")


class AdjudicatorFeedback(Submission):
    adjudicator = models.ForeignKey(Adjudicator)
    score = models.FloatField()
    agree_with_decision = models.NullBooleanField()
    comments = models.TextField(blank=True)

    source_adjudicator = models.ForeignKey(DebateAdjudicator, blank=True,
                                           null=True)
    source_team = models.ForeignKey(DebateTeam, blank=True, null=True)

    class Meta:
        unique_together = [('adjudicator', 'source_adjudicator', 'source_team', 'version')]

    @property
    def source(self):
        if self.source_adjudicator:
            return self.source_adjudicator.adjudicator
        if self.source_team:
            return self.source_team.team

    @property
    def debate(self):
        if self.source_adjudicator:
            return self.source_adjudicator.debate
        if self.source_team:
            return self.source_team.debate

    @property
    def round(self):
        return self.debate.round

    @property
    def feedback_weight(self):
        if self.round:
            return self.round.feedback_weight
        return 1

    def save(self, *args, **kwargs):
        if not (self.source_adjudicator or self.source_team):
            raise ValidationError("Either the source adjudicator or source team wasn't specified.")
        super(AdjudicatorFeedback, self).save(*args, **kwargs)


class AdjudicatorAllocation(object):
    def __init__(self, debate, chair=None, panel=None):
        self.debate = debate
        self.chair = chair
        self.panel = panel or []
        self.trainees = []

    @property
    def list(self):
        a = [self.chair]
        a.extend(self.panel)
        return a

    def __unicode__(self):
        return ", ".join(map(lambda x: (x is not None) and x.name or "<None>", self.list))

    def __iter__(self):
        yield DebateAdjudicator.TYPE_CHAIR, self.chair
        for a in self.panel:
            yield DebateAdjudicator.TYPE_PANEL, a
        for a in self.trainees:
            yield DebateAdjudicator.TYPE_TRAINEE, a

    def delete(self):
        """
        Delete existing, current allocation
        """

        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        self.chair = None
        self.panel = []
        self.trainees = []

    @property
    def has_chair(self):
        return self.chair is not None

    @property
    def is_panel(self):
        return len(self.panel) > 0

    @property
    def valid(self):
        return self.has_chair and len(self.panel) % 2 == 0

    def save(self):
        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        for t, adj in self:
            if isinstance(adj, Adjudicator):
                adj = adj.id
            if adj:
                DebateAdjudicator(
                    debate = self.debate,
                    adjudicator_id = adj,
                    type = t,
                ).save()


class BallotSubmission(Submission):
    """Represents a single submission of ballots for a debate.
    (Not a single motion, but a single submission of all ballots for a debate.)"""

    debate = models.ForeignKey(Debate)
    motion = models.ForeignKey('Motion', blank=True, null=True, on_delete=models.SET_NULL)

    copied_from = models.ForeignKey('BallotSubmission', blank=True, null=True)
    discarded = models.BooleanField(default=False)

    class Meta:
        unique_together = [('debate', 'version')]

    def __unicode__(self):
        return 'Ballot for ' + unicode(self.debate) + ' submitted at ' + unicode(self.timestamp.isoformat())

    @property
    def ballot_set(self):
        if not hasattr(self, "_ballot_set"):
            self._ballot_set = BallotSet(self)
        return self._ballot_set

    def clean(self):
        # The motion must be from the relevant round
        super(BallotSubmission, self).clean()
        if self.motion.round != self.debate.round:
                raise ValidationError("Debate is in round %d but motion (%s) is from round %d" % (self.debate.round, self.motion.reference, self.motion.round))
        if self.confirmed and self.discarded:
            raise ValidationError("A ballot can't be both confirmed and discarded!")

    def is_identical(self, other):
        """Returns True if all data fields are the same. Returns False in any
        other case. Does not raise exceptions if things look weird. Possibly
        over-conservative: it checks fields that are theoretically redundant."""
        if self.debate != other.debate:
            return False
        if self.motion != other.motion:
            return False
        def check(this, other_set, fields):
            """Returns True if it could find an object with the same data.
            Using filter() doesn't seem to work on non-integer float fields,
            so we compare score by retrieving it."""
            try:
                other_obj = other_set.get(**dict((f, getattr(this, f)) for f in fields))
            except (MultipleObjectsReturned, ObjectDoesNotExist):
                return False
            return this.score == other_obj.score
        # Check all of the SpeakerScoreByAdjs.
        # For each one, we must be able to find one by the same adjudicator, team and
        # position, and they must have the same score.
        for this in self.speakerscorebyadj_set.all():
            if not check(this, other.speakerscorebyadj_set, ["debate_adjudicator", "debate_team", "position"]):
                return False
        # Check all of the SpeakerScores.
        # In theory, we should only need to check speaker positions, since that is
        # the only information not inferrable from SpeakerScoreByAdj. But check
        # everything, to be safe.
        for this in self.speakerscore_set.all():
            if not check(this, other.speakerscore_set, ["debate_team", "speaker", "position"]):
                return False
        # Check TeamScores, to be safe
        for this in self.teamscore_set.all():
            if not check(this, other.teamscore_set, ["debate_team", "points"]):
                return False
        return True

    # For further discussion
    #submitter_name = models.CharField(max_length=40, null=True)                # only relevant for public submissions
    #submitter_email = models.EmailField(max_length=254, blank=True, null=True) # only relevant for public submissions
    #submitter_phone = models.CharField(max_length=40, blank=True, null=True)   # only relevant for public submissions


class SpeakerScoreByAdj(models.Model):
    """
    Holds score given by a particular adjudicator in a debate
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_adjudicator = models.ForeignKey(DebateAdjudicator)
    debate_team = models.ForeignKey(DebateTeam)
    score = ScoreField()
    position = models.IntegerField()

    class Meta:
        unique_together = [('debate_adjudicator', 'debate_team', 'position', 'ballot_submission')]

    @property
    def debate(self):
        return self.debate_team.debate


class TeamScore(models.Model):
    """
    Holds a teams total score and points in a debate
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey(DebateTeam)
    points = models.PositiveSmallIntegerField()
    score = ScoreField()

    class Meta:
        unique_together = [('debate_team', 'ballot_submission')]


class SpeakerScoreManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(SpeakerScoreManager,
                     self).get_queryset().select_related('speaker')


class SpeakerScore(models.Model):
    """
    Represents a speaker's score in a debate
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey(DebateTeam)
    speaker = models.ForeignKey(Speaker)
    score = ScoreField()
    position = models.IntegerField()

    objects = SpeakerScoreManager()

    class Meta:
        unique_together = [('debate_team', 'speaker', 'position', 'ballot_submission')]


class MotionManager(models.Manager):
    def statistics(self, round=None):
        if round is None:
            motions = self.all()
        else:
            motions = self.filter(round__seq__lte=round.seq)

        #motions = motions.filter(
            #ballotsubmission__confirmed = True
        #).annotate(
            #chosen_in = models.Count('ballotsubmission')
        #)
        # Need to do it using extra() in order to include the motions that haven't been done,
        # otherwise filter() leaves them out.
        motions = motions.extra({"chosen_in": """
                SELECT COUNT (*)
                FROM "debate_ballotsubmission"
                WHERE "debate_ballotsubmission"."confirmed" = True
                AND "debate_ballotsubmission"."motion_id" = "debate_motion"."id"
            """,
        })

        # TODO is there a more efficient way to do this?
        for motion in motions:
            ballots = BallotSubmission.objects.filter(confirmed=True, motion=motion)
            if motion.chosen_in == 0:
                motion.aff_wins = 0
                motion.aff_wins_percent = 0
                motion.neg_wins = 0
                motion.neg_wins_percent = 0
            else:
                motion.aff_wins = sum(ballot.ballot_set.aff_win for ballot in ballots)
                motion.aff_wins_percent = int((float(motion.aff_wins) / float(motion.chosen_in)) * 100)
                motion.neg_wins = sum(ballot.ballot_set.neg_win for ballot in ballots)
                motion.neg_wins_percent = int((float(motion.neg_wins) / float(motion.chosen_in)) * 100)

        return motions


class Motion(models.Model):
    """Represents a single motion (not a set of motions)."""

    seq = models.IntegerField(help_text="The order in which motions display")
    text = models.CharField(max_length=500, help_text="The motion itself")
    reference = models.CharField(max_length=100, help_text="Shortcode for the motion")
    flagged = models.BooleanField(default=False, help_text="WADL: Allows for particular motions to be flagged as contentious")
    round = models.ForeignKey(Round)
    objects = MotionManager()

    def __unicode__(self):
        return self.text


class DebateTeamMotionPreference(models.Model):
    """Represents a motion preference submitted by a debate team."""
    debate_team = models.ForeignKey(DebateTeam)
    motion = models.ForeignKey(Motion)
    preference = models.IntegerField()
    ballot_submission = models.ForeignKey(BallotSubmission)

    class Meta:
        unique_together = [('debate_team', 'preference', 'ballot_submission')]


class ActionLogManager(models.Manager):
    def log(self, *args, **kwargs):
        obj = self.model(*args, **kwargs)
        obj.full_clean()
        obj.save()


class ActionLog(models.Model):
    # These aren't generated automatically - all generations of these should
    # be done in views (not models).

    # TODO update these to account for new ballot submissions model

    ACTION_TYPE_BALLOT_CHECKIN          = 10
    ACTION_TYPE_BALLOT_CREATE           = 11
    ACTION_TYPE_BALLOT_CONFIRM          = 12
    ACTION_TYPE_BALLOT_DISCARD          = 13
    ACTION_TYPE_BALLOT_SUBMIT           = 14
    ACTION_TYPE_BALLOT_EDIT             = 15
    ACTION_TYPE_FEEDBACK_SUBMIT         = 20
    ACTION_TYPE_FEEDBACK_SAVE           = 21
    ACTION_TYPE_TEST_SCORE_EDIT         = 22
    ACTION_TYPE_DRAW_CREATE             = 30
    ACTION_TYPE_DRAW_CONFIRM            = 31
    ACTION_TYPE_ADJUDICATORS_SAVE       = 32
    ACTION_TYPE_VENUES_SAVE             = 33
    ACTION_TYPE_DRAW_RELEASE            = 34
    ACTION_TYPE_DRAW_UNRELEASE          = 35
    ACTION_TYPE_MOTION_EDIT             = 40
    ACTION_TYPE_MOTIONS_RELEASE         = 41
    ACTION_TYPE_MOTIONS_UNRELEASE       = 42
    ACTION_TYPE_DEBATE_IMPORTANCE_EDIT  = 50
    ACTION_TYPE_ROUND_START_TIME_SET    = 60
    ACTION_TYPE_AVAIL_TEAMS_SAVE        = 80
    ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE = 81
    ACTION_TYPE_AVAIL_VENUES_SAVE       = 82
    ACTION_TYPE_CONFIG_EDIT             = 90

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_BALLOT_DISCARD         , 'Discarded ballot set'),
        (ACTION_TYPE_BALLOT_CHECKIN         , 'Checked in ballot set'),
        (ACTION_TYPE_BALLOT_CREATE          , 'Created ballot set'), # For tab monkeys, not debaters
        (ACTION_TYPE_BALLOT_EDIT            , 'Edited ballot set'),
        (ACTION_TYPE_BALLOT_CONFIRM         , 'Confirmed ballot set'),
        (ACTION_TYPE_BALLOT_SUBMIT          , 'Submitted ballot set from the public form'), # For debaters, not tab monkeys
        (ACTION_TYPE_FEEDBACK_SUBMIT        , 'Submitted feedback from the public form'), # For debaters, not tab monkeys
        (ACTION_TYPE_FEEDBACK_SAVE          , 'Saved feedback'), # For tab monkeys, not debaters
        (ACTION_TYPE_TEST_SCORE_EDIT        , 'Edited adjudicator test score'),
        (ACTION_TYPE_ADJUDICATORS_SAVE      , 'Saved adjudicator allocation'),
        (ACTION_TYPE_VENUES_SAVE            , 'Saved venues'),
        (ACTION_TYPE_DRAW_CREATE            , 'Created draw'),
        (ACTION_TYPE_DRAW_CONFIRM           , 'Confirmed draw'),
        (ACTION_TYPE_DRAW_RELEASE           , 'Released draw'),
        (ACTION_TYPE_DRAW_UNRELEASE         , 'Unreleased draw'),
        (ACTION_TYPE_MOTION_EDIT            , 'Added/edited motion'),
        (ACTION_TYPE_MOTIONS_RELEASE        , 'Released motions'),
        (ACTION_TYPE_MOTIONS_UNRELEASE      , 'Unreleased motions'),
        (ACTION_TYPE_DEBATE_IMPORTANCE_EDIT , 'Edited debate importance'),
        (ACTION_TYPE_ROUND_START_TIME_SET   , 'Set start time'),
        (ACTION_TYPE_AVAIL_TEAMS_SAVE       , 'Edited teams availability'),
        (ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE, 'Edited adjudicators availability'),
        (ACTION_TYPE_AVAIL_VENUES_SAVE      , 'Edited venue availability'),
        (ACTION_TYPE_CONFIG_EDIT            , 'Edited tournament configuration'),
    )

    REQUIRED_FIELDS_BY_ACTION_TYPE = {
        ACTION_TYPE_BALLOT_DISCARD         : ('ballot_submission',),
        ACTION_TYPE_BALLOT_CHECKIN         : ('debate',), # not ballot_submission
        ACTION_TYPE_BALLOT_CREATE          : ('ballot_submission',),
        ACTION_TYPE_BALLOT_EDIT            : ('ballot_submission',),
        ACTION_TYPE_BALLOT_CONFIRM         : ('ballot_submission',),
        ACTION_TYPE_BALLOT_SUBMIT          : ('ballot_submission',),
        ACTION_TYPE_FEEDBACK_SUBMIT        : ('adjudicator_feedback',),
        ACTION_TYPE_FEEDBACK_SAVE          : ('adjudicator_feedback',),
        ACTION_TYPE_TEST_SCORE_EDIT        : ('adjudicator_test_score_history',),
        ACTION_TYPE_ADJUDICATORS_SAVE      : ('round',),
        ACTION_TYPE_VENUES_SAVE            : ('round',),
        ACTION_TYPE_DRAW_CREATE            : ('round',),
        ACTION_TYPE_DRAW_CONFIRM           : ('round',),
        ACTION_TYPE_DRAW_RELEASE           : ('round',),
        ACTION_TYPE_DRAW_UNRELEASE         : ('round',),
        ACTION_TYPE_DEBATE_IMPORTANCE_EDIT : ('debate',),
        ACTION_TYPE_ROUND_START_TIME_SET   : ('round',),
        ACTION_TYPE_MOTION_EDIT            : ('motion',),
        ACTION_TYPE_MOTIONS_RELEASE        : ('round',),
        ACTION_TYPE_MOTIONS_UNRELEASE      : ('round',),
        ACTION_TYPE_CONFIG_EDIT            : (),
        ACTION_TYPE_AVAIL_TEAMS_SAVE       : ('round',),
        ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE: ('round',),
        ACTION_TYPE_AVAIL_VENUES_SAVE      : ('round',),
    }

    ALL_OPTIONAL_FIELDS = ('debate', 'ballot_submission', 'adjudicator_feedback', 'round', 'motion')

    type = models.PositiveSmallIntegerField(choices=ACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    debate = models.ForeignKey(Debate, blank=True, null=True)
    ballot_submission = models.ForeignKey(BallotSubmission, blank=True, null=True)
    adjudicator_test_score_history = models.ForeignKey(AdjudicatorTestScoreHistory, blank=True, null=True)
    adjudicator_feedback = models.ForeignKey(AdjudicatorFeedback, blank=True, null=True)
    round = models.ForeignKey(Round, blank=True, null=True)
    motion = models.ForeignKey(Motion, blank=True, null=True)

    objects = ActionLogManager()

    def __repr__(self):
        return '<Action %d by %s (%s): %s>' % (self.id, self.user, self.timestamp, self.get_type_display())

    def clean(self):
        required_fields = self.REQUIRED_FIELDS_BY_ACTION_TYPE[self.type]
        errors = list()
        for field_name in self.ALL_OPTIONAL_FIELDS:
            if field_name in required_fields:
                if getattr(self, field_name) is None:
                    errors.append(ValidationError('A log entry of type "%s" requires the field "%s".' %
                        (self.get_type_display(), field_name)))
            else:
                if getattr(self, field_name) is not None:
                    errors.append(ValidationError('A log entry of type "%s" must not have the field "%s".' %
                        (self.get_type_display(), field_name)))
        if self.user is None and self.ip_address is None:
            errors.append(ValidationError('All log entries require at least one of a user and an IP address.'))
        if errors:
            raise ValidationError(errors)

    def get_parameters_display(self):
        required_fields = self.REQUIRED_FIELDS_BY_ACTION_TYPE[self.type]
        strings = list()
        for field_name in required_fields:
            try:
                value = getattr(self, field_name)
                if field_name == 'ballot_submission':
                    strings.append('%s vs %s' % (value.debate.aff_team, value.debate.neg_team))
                elif field_name == 'debate':
                    strings.append('%s vs %s' % (value.aff_team, value.neg_team))
                elif field_name == 'round':
                    strings.append('round %s' % value.seq)
                elif field_name == 'motion':
                    strings.append(value.reference)
                elif field_name == 'adjudicator_test_score_history':
                    strings.append(value.adjudicator.name + " (" + str(value.score) + ")")
                elif field_name == 'adjudicator_feedback':
                    strings.append(value.adjudicator.name)
                else:
                    strings.append(unicode(value))
            except AttributeError:
                strings.append("Unknown " + field_name)
        return ", ".join(strings)


class ConfigManager(models.Manager):
    def set(self, tournament, key, value):
        obj, created = self.get_or_create(tournament=tournament, key=key)
        obj.value = value
        obj.save()

    def get_(self, tournament, key, default=None):
        try:
            return self.get(tournament=tournament, key=key).value
        except ObjectDoesNotExist:
            return default


class Config(models.Model):
    tournament = models.ForeignKey(Tournament)
    key = models.CharField(max_length=40, unique=True)
    value = models.CharField(max_length=40)

    objects = ConfigManager()
