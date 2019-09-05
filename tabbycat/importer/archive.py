from statistics import mean
from xml.etree.ElementTree import Element, SubElement

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, Q
from django.utils.text import slugify

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from draw.models import Debate, DebateTeam
from motions.models import DebateTeamMotionPreference, Motion
from options.presets import (AustralianEastersPreferences, AustralsPreferences, BritishParliamentaryPreferences,
                             CanadianParliamentaryPreferences, JoyntPreferences, NZEastersPreferences, save_presets,
                             UADCPreferences, WADLPreferences, WSDCPreferences)
from participants.emoji import EMOJI_BY_NAME
from participants.models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team
from results.models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, Submission, TeamScore
from results.prefetch import populate_confirmed_ballots, populate_wins
from results.result import (BaseConsensusDebateResultWithSpeakers, BaseDebateResultWithSpeakers,
                            BaseEliminationDebateResult, DebateResult, VotingDebateResult)
from tournaments.models import Round, Tournament
from venues.models import Venue


# As ID/IDREF(S) must be unique to the whole document, prefix IDs
ADJ_PREFIX = "A"
MOTION_PREFIX = "M"
DEBATE_PREFIX = "D"
TEAM_PREFIX = "T"
SPEAKER_PREFIX = "S"
SPEAKER_CATEGORY_PREFIX = "SC"
BREAK_CATEGORY_PREFIX = "BC"
VENUE_PREFIX = "V"
INST_PREFIX = "I"
QUESTION_PREFIX = "Q"


class Exporter:

    def __init__(self, tournament):
        self.t = tournament
        self.root = Element('tournament', {'name': tournament.name, 'short': tournament.short_name})

    def create_all(self):
        self.add_rounds()
        self.add_participants()
        self.add_break_categories()
        self.add_institutions()
        self.add_motions()
        self.add_venues()
        self.add_questions()

        return self.root

    def add_rounds(self):
        results_prefetch = Prefetch('ballotsubmission_set', queryset=BallotSubmission.objects.filter(confirmed=True).prefetch_related(
            'speakerscore_set', 'speakerscorebyadj_set', 'teamscore_set'))
        veto_prefetch = Prefetch('debateteammotionpreference_set', queryset=DebateTeamMotionPreference.objects.filter(
            preference=3, ballot_submission__confirmed=True
        ))
        dt_prefetch = Prefetch('debateteam_set', queryset=DebateTeam.objects.all().select_related(
            'team', 'team__institution'
        ).prefetch_related(veto_prefetch))
        debate_prefetch = Prefetch('debate_set', queryset=Debate.objects.all().prefetch_related(
            'debateadjudicator_set', dt_prefetch, results_prefetch
        ))

        for round in self.t.round_set.all().prefetch_related(debate_prefetch, 'motion_set').order_by('seq'):
            populate_confirmed_ballots(round.debate_set.all(), motions=True, results=True)
            populate_wins(round.debate_set.all())

            round_tag = SubElement(self.root, 'round', {
                'name': round.name,
                'elimination': str(round.stage == Round.STAGE_ELIMINATION),
                'feedback-weight': str(round.feedback_weight)
            })

            if round.stage == Round.STAGE_ELIMINATION:
                round_tag.set('break-category', BREAK_CATEGORY_PREFIX + str(round.break_category_id))

            if round.starts_at is not None and round.starts_at != "":
                round_tag.set('start', str(round.starts_at))

            motion = round.motion_set.first()

            for debate in round.debate_set.all():
                self.add_debates(round_tag, motion, debate)

    def add_debates(self, round_tag, motion, debate):
        debate_tag = SubElement(round_tag, 'debate', {
            'id': DEBATE_PREFIX + str(debate.id)
        })

        # Add list of motions as attribute
        adjs = " ".join([ADJ_PREFIX + str(d_adj.adjudicator_id) for d_adj in debate.debateadjudicator_set.all()])
        if adjs != "":
            debate_tag.set('adjudicators', adjs)

            chair = debate.debateadjudicator_set.get(type=DebateAdjudicator.TYPE_CHAIR).adjudicator_id
            debate_tag.set('chair', ADJ_PREFIX + str(chair))

        # Venue
        if debate.venue_id is not None:
            debate_tag.set('venue', VENUE_PREFIX + str(debate.venue_id))

        # Motion is optional
        if self.t.pref('enable_motions') and debate.confirmed_ballot is not None:
            motion = debate.confirmed_ballot.motion
        if motion is not None:
            debate_tag.set('motion', MOTION_PREFIX + str(motion.id))

        if debate.confirmed_ballot is not None:
            result = DebateResult(debate.confirmed_ballot, tournament=self.t)

            for side in self.t.sides:
                side_tag = SubElement(debate_tag, 'side', {
                    'team': TEAM_PREFIX + str(debate.get_team(side).id)
                })

                dt = debate.get_dt(side)
                if dt.debateteammotionpreference_set.exists():
                    side_tag.set('motion-veto', MOTION_PREFIX + str(dt.debateteammotionpreference_set.first().motion_id))

                if isinstance(result, VotingDebateResult):
                    for (adj, scoresheet) in result.scoresheets.items():
                        self.add_team_ballots(side_tag, result, adj, scoresheet, side)
                elif isinstance(result, BaseEliminationDebateResult):
                    adv = side in result.advancing_sides()
                    ballot_tag = SubElement(side_tag, 'ballot', {
                        'adjudicators': adjs,
                        'rank': str(1 if adv else 2),
                        'ignored': 'False'
                    })
                    ballot_tag.text = str(adv)
                else:
                    self.add_team_ballots(
                        side_tag,
                        result,
                        adjs,
                        result.scoresheet,
                        side
                    )

                if isinstance(result, BaseDebateResultWithSpeakers):
                    self.add_speakers(side_tag, debate, result, side)

    def add_team_ballots(self, side_tag, result, adj, scoresheet, side):
        ballot_tag = SubElement(side_tag, 'ballot')

        if isinstance(result, VotingDebateResult):
            majority = result.majority_adjudicators()

            ballot_tag.set('adjudicators', ADJ_PREFIX + str(adj.id))

            minority = adj not in majority
            ballot_tag.set('minority', str(minority))
            ballot_tag.set('ignored', str(minority and not self.t.pref('margin_includes_dissenters')))
        else:
            ballot_tag.set('adjudicators', adj)
            ballot_tag.set('ignored', 'False')

        if hasattr(scoresheet, 'winner'):
            ballot_tag.set('rank', str(1 if scoresheet.winner() == side else 2))
        else:
            ballot_tag.set('rank', str(scoresheet.rank(side)))

        if hasattr(scoresheet, 'advancing_sides'):
            ballot_tag.text = str(side in scoresheet.advancing_sides())
        else:
            ballot_tag.text = str(scoresheet.get_total(side))

    def add_speakers(self, side_tag, debate, result, side):
        for pos in self.t.positions:
            speaker = result.get_speaker(side, pos)

            if speaker is not None:
                speech_tag = SubElement(side_tag, 'speech', {
                    'speaker': SPEAKER_PREFIX + str(result.get_speaker(side, pos).id),
                    'reply': str(pos > self.t.pref('substantive_speakers'))
                })

                if isinstance(result, BaseConsensusDebateResultWithSpeakers):
                    ballot_tag = SubElement(speech_tag, 'ballot', {
                        'adjudicators': " ".join([ADJ_PREFIX + str(d_adj.adjudicator_id) for d_adj in debate.debateadjudicator_set.all()])
                    })
                    ballot_tag.text = str(result.scoresheet.get_score(side, pos))
                else:
                    for (adj, scoresheet) in result.scoresheets.items():
                        ballot_tag = SubElement(speech_tag, 'ballot', {
                            'adjudicators': ADJ_PREFIX + str(adj.id)
                        })
                        ballot_tag.text = str(scoresheet.get_score(side, pos))

    def add_participants(self):
        participants_tag = SubElement(self.root, 'participants')

        speaker_category_prefetch = Prefetch('speaker_set', queryset=Speaker.objects.all().prefetch_related('categories'))
        for team in self.t.team_set.all().prefetch_related(speaker_category_prefetch, 'break_categories'):
            team_tag = SubElement(participants_tag, 'team', {
                'name': team.long_name,
                'code': team.code_name,
                'id': TEAM_PREFIX + str(team.id)
            })

            team_tag.set('break-eligibilities', " ".join([BREAK_CATEGORY_PREFIX + str(bc.id) for bc in team.break_categories.all()]))

            for speaker in team.speaker_set.all():
                speaker_tag = SubElement(team_tag, 'speaker', {
                    'id': SPEAKER_PREFIX + str(speaker.id)
                })
                speaker_tag.text = speaker.name

                if team.institution is not None:
                    speaker_tag.set('institutions', INST_PREFIX + str(team.institution_id))

                if speaker.gender != "":
                    speaker_tag.set('gender', speaker.gender)

                speaker_tag.set('categories', " ".join([SPEAKER_CATEGORY_PREFIX + str(sc.id) for sc in speaker.categories.all()]))

        for adj in self.t.relevant_adjudicators.prefetch_related('adjudicatorfeedback_set'):
            adj_tag = SubElement(participants_tag, 'adjudicator', {
                'id': ADJ_PREFIX + str(adj.id),
                'name': adj.name,
                'core': str(adj.adj_core),
                'independent': str(adj.independent),
                'score': str(adj.test_score)
            })

            if adj.institution is not None:
                adj_tag.set('institutions', INST_PREFIX + str(adj.institution_id))

            if adj.gender != "":
                adj_tag.set('gender', adj.gender)

            for feedback in adj.adjudicatorfeedback_set.filter(confirmed=True):
                feedback_tag = SubElement(adj_tag, 'feedback', {
                    'score': str(feedback.score)
                })
                if feedback.source_adjudicator is not None:
                    feedback_tag.set('source-adjudicator', ADJ_PREFIX + str(feedback.source_adjudicator.adjudicator_id))
                    feedback_tag.set('debate', DEBATE_PREFIX + str(feedback.source_adjudicator.debate_id))
                else:
                    feedback_tag.set('source-team', TEAM_PREFIX + str(feedback.source_team.team_id))
                    feedback_tag.set('debate', DEBATE_PREFIX + str(feedback.source_team.debate_id))

                for question in self.t.adjudicatorfeedbackquestion_set.all():
                    try:
                        answer = AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[question.answer_type].objects.get(
                            feedback=feedback,
                            question=question
                        )
                    except ObjectDoesNotExist:
                        continue

                    answer_tag = SubElement(feedback_tag, 'answer', {
                        'question': QUESTION_PREFIX + str(answer.question_id)
                    })
                    answer_tag.text = str(answer.answer)

    def add_break_categories(self):
        speaker_categories = self.t.speakercategory_set.all().order_by('seq')

        for category in speaker_categories:
            sc_tag = SubElement(self.root, 'speaker-category', {
                'id': SPEAKER_CATEGORY_PREFIX + str(category.id),
            })
            sc_tag.text = category.name

        break_categories = self.t.breakcategory_set.all().order_by('seq')

        for category in break_categories:
            bc_tag = SubElement(self.root, 'break-category', {
                'id': BREAK_CATEGORY_PREFIX + str(category.id)
            })
            bc_tag.text = category.name

    def add_institutions(self):
        institution_query = Institution.objects.filter(
            Q(id__in=self.t.relevant_adjudicators.values_list('institution_id')) |
            Q(id__in=self.t.team_set.all().values_list('institution_id'))
        ).select_related('region')
        for institution in institution_query:
            institution_tag = SubElement(self.root, 'institution', {
                'id': INST_PREFIX + str(institution.id),
                'reference': institution.code
            })
            institution_tag.text = institution.name

            if institution.region is not None:
                institution_tag.set('region', institution.region.name)

    def add_motions(self):
        for motion in Motion.objects.filter(round__tournament=self.t):
            motion_tag = SubElement(self.root, 'motion', {
                'id': MOTION_PREFIX + str(motion.id),
                'reference': motion.reference
            })

            if motion.info_slide != '':
                info_slide = SubElement(motion_tag, 'info-slide')
                info_slide.text = motion.info_slide

            motion_tag.text = motion.text

    def add_venues(self):
        for venue in self.t.relevant_venues:
            venue_tag = SubElement(self.root, 'venue', {
                'id': VENUE_PREFIX + str(venue.id)
            })
            venue_tag.text = venue.name

    def add_questions(self):
        for question in self.t.adjudicatorfeedbackquestion_set.all():
            question_tag = SubElement(self.root, 'question', {
                'id': QUESTION_PREFIX + str(question.id),
                'name': question.name,
                'from-teams': str(question.from_team),
                'from-adjudicators': str(question.from_adj),
                'type': question.answer_type
            })
            question_tag.text = question.text


class Importer:

    def __init__(self, tournament):
        self.root = tournament

    def import_tournament(self):
        self.tournament = Tournament(name=self.root.get('name'))

        if self.root.get('short') is not None:
            self.tournament.short_name = self.root.get('short')
            self.tournament.slug = slugify(self.root.get('short'))
        else:
            self.tournament.short_name = self.root.get('name')[:25]
            self.tournament.slug = slugify(self.root.get('name')[:50])
        self.tournament.save()

        # Import all the separate parts
        self.set_preferences()
        self.import_institutions()
        self.import_categories()
        self.import_venues()
        self.import_questions()
        self.import_teams()
        self.import_speakers()
        self.import_adjudicators()
        self.import_debates()
        self.import_motions()
        self.import_results()
        self.import_feedback()

    def _is_consensus_ballot(self, elimination):
        xpath = "round[@elimination='" + elimination + "']/debate/side"
        return len(self.root.findall(xpath + "/ballot")) == len(self.root.findall(xpath))

    def set_preferences(self):
        styles = {
            "apda": None,
            "asians": None,
            "aus-easters": AustralianEastersPreferences,
            "australs": AustralsPreferences,
            "bp": BritishParliamentaryPreferences,
            "cndc": None,
            "cp": CanadianParliamentaryPreferences,
            "ffd": None,
            "joynt": JoyntPreferences,
            "npda": None,
            "nz-easters": NZEastersPreferences,
            "opd": None,
            "paris-v": None,
            "uadc": UADCPreferences,
            "wadl": WADLPreferences,
            "wsdc": WSDCPreferences,
            "": None
        }
        if self.root.get('style') is not None and styles[self.root.get('style', '')] is not None:
            style = styles[self.root.get('style')]
            save_presets(self.tournament, style)
            self.preliminary_consensus = style.debate_rules__ballots_per_debate_prelim == 'per-debate'
            self.elimination_consensus = style.debate_rules__ballots_per_debate_elim == 'per-debate'
            return True # Exit method

        self.is_bp = len(self.root.find('round').find('debate').findall('side')) == 4
        if self.is_bp:
            self.preliminary_consensus = True
            self.elimination_consensus = True
            save_presets(self.tournament, BritishParliamentaryPreferences)
        else:
            self.preliminary_consensus = self._is_consensus_ballot('False')
            self.elimination_consensus = self._is_consensus_ballot('True')
            substantive_speakers = len(self.root.find('round').find('debate').find('side').findall("speech[@reply='False']"))
            reply_scores_enabled = len(self.root.findall("round/debate/side/speech[@reply='True']")) != 0
            margin_includes_dissenters = len(self.root.findall("round/debate/side/ballot[@minority='True'][@ignored='True']")) == 0

            self.tournament.preferences['debate_rules__substantive_speakers'] = substantive_speakers
            self.tournament.preferences['debate_rules__reply_scores_enabled'] = reply_scores_enabled
            self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate' if self.preliminary_consensus else 'per-adj'
            self.tournament.preferences['debate_rules__ballots_per_debate_elim'] = 'per-debate' if self.elimination_consensus else 'per-adj'
            self.tournament.preferences['scoring__margin_includes_dissenters'] = margin_includes_dissenters

    def import_institutions(self):
        self.institutions = {}
        self.regions = {}

        for institution in self.root.findall('institution'):
            # Use get_or_create as institutions may be shared between tournaments
            inst_obj, created = Institution.objects.get_or_create(
                code=institution.get('reference'), name=institution.text
            )
            self.institutions[institution.get('id')] = inst_obj

            if institution.get('region') is not None:
                region = institution.get('region')
                if region not in self.regions:
                    self.regions[region] = Region.objects.get_or_create(name=region)

                inst_obj.region = self.regions[region]
                inst_obj.save()

    def import_categories(self):
        self.team_breaks = {}
        self.speaker_categories = {}

        for i, breakqual in enumerate(self.root.findall('break-category'), 1):
            bc = BreakCategory(
                tournament=self.tournament, name=breakqual.text,
                slug=slugify(breakqual.text[:50]), seq=i,
                break_size=0, is_general=False, priority=0
            )
            bc.save()
            self.team_breaks[breakqual.get('id')] = bc

        for i, category in enumerate(self.root.findall('speaker-category'), 1):
            sc = SpeakerCategory(
                tournament=self.tournament, name=category.text,
                slug=slugify(category.text[:50]), seq=i
            )
            sc.save()
            self.speaker_categories[category.get('id')] = sc

    def import_venues(self):
        self.venues = {}

        for venue in self.root.findall('venue'):
            v = Venue(tournament=self.tournament, name=venue.text, priority=venue.get('priority', 0))
            v.save()
            self.venues[venue.get('id')] = v

    def import_questions(self):
        self.questions = {}

        for i, question in enumerate(self.root.findall('question'), 1):
            q = AdjudicatorFeedbackQuestion(
                tournament=self.tournament, seq=i, text=question.text,
                name=question.get('name'), reference=slugify(question.get('name')[:50]),
                from_adj=question.attrib['from-adjudicators'], from_team=question.get('from-teams'),
                answer_type=question.get('type'), required=False
            )
            q.save()
            self.questions[question.get('id')] = q

    def import_teams(self):
        self.teams = {}
        for team in self.root.find('participants').findall('team'):
            team_obj = Team(tournament=self.tournament, long_name=team.get('name'))
            self.teams[team.get('id')] = team_obj

            # Get emoji & code name
            if 'code' in team.attrib:
                team_obj.code_name = team.get('code')
            emoji = EMOJI_BY_NAME.get(team.get('code'))
            if emoji is not None:
                team_obj.emoji = emoji

            # Find institution from speakers - Get first institution from each speaker to compare
            p_institutions = set([p.get('institutions').split(" ")[0] for p in team.findall('speaker')])
            team_institution = list(p_institutions)[0]

            if len(p_institutions) == 1 and team_institution is not None:
                team_obj.institution = self.institutions[team_institution]

            # Remove institution from team name
            if team_obj.institution is not None and team_obj.long_name.startswith(team_obj.institution.name + " "):
                team_obj.reference = team_obj.long_name[len(team_obj.institution.name) + 1:]
                team_obj.short_name = team_obj.institution.code + " " + team_obj.reference
                team_obj.use_institution_prefix = True
            else:
                team_obj.reference = team_obj.long_name
                team_obj.short_name = team_obj.reference[:50]
            team_obj.short_reference = team_obj.reference[:35]
            team.obj.save()

            # Break eligibilities
            for bc in team.get('break-eligibilities', "").split():
                team_obj.break_categories.add(self.team_breaks[bc])

    def import_speakers(self):
        self.speakers = {}

        for team in self.root.find('participants').findall('team'):
            for speaker in team.findall('speaker'):
                speaker_obj = Speaker(team=self.teams[team.get('id')], name=speaker.text, gender=speaker.get('gender', ''))
                speaker_obj.save()
                self.speakers[speaker.get('id')] = speaker_obj

                for sc in speaker.get('categories', "").split():
                    speaker_obj.categories.add(self.speaker_categories[sc])

    def import_adjudicators(self):
        self.adjudicators = {}

        for adj in self.root.find('participants').findall('adjudicator'):
            adj_obj = Adjudicator(
                tournament=self.tournament, test_score=adj.get('score', 0),
                institution=self.institutions.get(adj.get('institutions', "").split()[0]),
                independent=adj.get('independent', False), adj_core=adj.get('core', False),
                name=adj.get('name'), gender=adj.get('gender', ''))
            adj_obj.save()
            self.adjudicators[adj.get('id')] = adj_obj

    def _get_voting_adjs(self, debate):
        voting_adjs = set()
        for ballot in debate.findall('.//ballot'):
            voting_adjs.update(ballot.get('adjudicators').split())
        return voting_adjs

    def import_debates(self):
        self.debates = {}
        self.debateteams = {}
        self.debateadjudicators = {}

        rounds = []
        for i, round in enumerate(self.root.findall('round'), 1):
            round_stage = Round.STAGE_ELIMINATION if round.get('elimination', 'False') == 'True' else Round.STAGE_PRELIMINARY
            draw_type = Round.DRAW_ELIMINATION if round_stage == Round.STAGE_ELIMINATION else Round.DRAW_MANUAL

            round_obj = Round(
                tournament=self.tournament, seq=i, completed=True, name=round.get('name'),
                abbreviation=round.get('name')[:10], stage=round_stage, draw_type=draw_type,
                draw_status=Round.STATUS_RELEASED, feedback_weight=round.get('feedback-weight', 0),
                starts_at=round.get('start')
            )
            rounds.append(round_obj)

            if round_stage == Round.STAGE_ELIMINATION:
                round_obj.break_category = self.team_breaks.get(round.get('break-category'))
            round_obj.save()

            side_start = 2 if self.is_bp else 0

            for debate in round.findall('debate'):
                debate_obj = Debate(round=round_obj, venue=self.venues.get(debate.get('venue')), result_status=Debate.STATUS_CONFIRMED)
                debate_obj.save()
                self.debates[debate.get('id')] = debate_obj

                # Debate-teams
                for i, side in enumerate(debate.findall('side'), side_start):
                    position = DebateTeam.SIDE_CHOICES[i][0]
                    debateteam_obj = DebateTeam(debate=debate_obj, team=self.teams[side.get('team')], side=position)
                    debateteam_obj.save()
                    self.debateteams[(debate.get('id'), side.get('team'))] = debateteam_obj

                # Debate-adjudicators
                voting_adjs = self._get_voting_adjs(debate)
                for adj in debate.get('adjudicators').split():
                    adj_type = DebateAdjudicator.TYPE_PANEL if adj in voting_adjs else DebateAdjudicator.TYPE_TRAINEE
                    if debate.get('chair') == adj:
                        adj_type = DebateAdjudicator.TYPE_CHAIR
                    adj_obj = DebateAdjudicator(debate=debate_obj, adjudicator=self.adjudicators[adj], type=adj_type)
                    self.debateadjudicators[(debate.get('id'), adj)] = adj_obj

    def import_motions(self):
        # Can cause data consistency problems if motions are re-used between rounds: See #645
        self.motions = {}

        motions_by_round = {}
        seq_by_round = {}
        for r_obj, round in zip(self.tournament.round_set.all().order_by('seq'), self.root.findall('round')):
            motions_by_round[r_obj.id] = set()
            seq_by_round[r_obj.id] = 1
            for debate in round.findall('debate'):
                motions_by_round[r_obj.id].add(debate.get('motion'))

        for motion in self.root.findall('motion'):
            for r, m_set in motions_by_round.items():
                if motion.get('id') in m_set:
                    motion_obj = Motion(
                        seq=seq_by_round[r], text=motion.text, reference=motion.get('reference'),
                        info_slide=getattr(motion.find('info-slide'), 'text', ''), round_id=r
                    )
                    motion_obj.save()
                    self.motions[motion.get('id')] = motion_obj

    def _get_margin(self, debate):
        side_ts = []
        for side in debate.findall('side'):
            scores = []
            for b in side.findall("ballot[@ignored='False']"):
                try:
                    scores.append(float(b.text))
                except ValueError:
                    continue
            side_ts.append(mean(scores))
        return (max(side_ts), max(side_ts) - min(side_ts))

    def _get_adj_split(self, debate, numeric):
        split = [0, 0, 0, 0]
        side_ballot_by_adj = {adj: [] for adj in self._get_voting_adjs(debate)}
        for side in debate.findall('side'):
            for ballot in side.findall('ballot'):
                for adj in ballot.get('adjudicators').split():
                    if numeric:
                        side_ballot_by_adj[adj] = float(ballot.text)
                    else:
                        side_ballot_by_adj[adj] = int(ballot.text == 'True')
        for adj, scores in side_ballot_by_adj.items():
            max_score = max(scores)
            for i, score in enumerate(split):
                if score == max_score:
                    split[i] += 1
        return (split, len(side_ballot_by_adj))

    def import_results(self):
        for round in self.root.findall('round'):
            consensus = self.preliminary_consensus if round.get('elimination') == 'False' else self.elimination_consensus

            for debate in round.findall('debate'):
                bs_obj = BallotSubmission(
                    version=1, submitter_type=Submission.SUBMITTER_TABROOM, confirmed=True,
                    debate=self.debates[debate.get('id')], motion=self.motions.get(debate.get('motion'))
                )
                ballotsubmissions.append(bs_obj)

                ts_max, ts_margin = (0, 0)
                numeric_scores = True
                try:
                    float(debate.find("side/ballot").text)
                except ValueError:
                    numeric_scores = False

                if not self.is_bp and numeric_scores:
                    ts_max, ts_margin = self._get_margin(debate)

                adj_split, num_adjs = (None, None)
                if not consensus:
                    adj_split, num_adjs = self._get_adj_split(debate, numeric_scores)

                for i, side in enumerate(debate.findall('side')):
                    dt = self.debateteams.get((debate.get('id'), side.get('team')))

                    if side.get('motion-veto') is not None:
                        motion_veto = DebateTeamMotionPreference(
                            debate_team=dt, motion=self.motions.get(side.get('motion-veto')), preference=3
                        )
                        motion_vetos_bs.append((motion_veto, bs_obj))

                    team_ballot = side.find("ballot[@ignored='False']")
                    points = 4 - int(team_ballot.get('rank')) if self.is_bp else 2 - int(team_ballot.get('rank'))

                    not_ignored = side.findall("ballot[@ignored='False']")

                    ts_obj = TeamScore(debate_team=dt, points=points)
                    teamscores.append((ts_obj, bs_obj))

                    if not self.is_bp:
                        ts_obj.win = points == 1

                    if numeric_scores:
                        scores = []
                        for b in not_ignored:
                            try:
                                scores.append(float(b.text))
                            except ValueError:
                                continue
                        ts_obj.score = mean(scores)
                        if not self.is_bp:
                            ts_obj.margin = ts_margin if float(team_ballot.text) == ts_max else -ts_margin
                    else:
                        ts_obj.win = team_ballot.text # Boolean for advancing otherwise

                    if consensus:
                        ts_obj.votes_given = 1 if ts_obj.win else 0
                        ts_obj.votes_possible = 1
                    else:
                        ts_obj.votes_given = adj_split[i]
                        ts_obj.votes_possible = num_adjs

                    for i, speech in enumerate(side.findall('speech'), 1):
                        ss_obj = None
                        if consensus:
                            speech_ballot = speech.find('ballot')

                            ss_obj = SpeakerScore(debate_team=dt, speaker=self.speakers[speech.get('speaker')],
                                score=float(speech_ballot.text), position=i)
                        else:
                            speech_ballots = speech.findall('ballot')
                            for speech_ballot in speech_ballots:
                                d_adj = self.debateadjudicators.get((debate.get('id'), speech_ballot.get('adjudicators')))
                                ss_adj_obj = SpeakerScoreByAdj(debate_adjudicator=d_adj,
                                    debate_team=dt, score=float(speech_ballot.text), position=i)
                                speakerscores_adj.append((ss_adj_obj, bs_obj))

                            included_adjs = [b.get('adjudicators') for b in not_ignored]
                            ss_obj = SpeakerScore(debate_team=dt, speaker=self.speakers[speech.get('speaker')], position=i,
                                score=mean([float(b.score) for b in speech_ballots if b.adjudicators in included_adjs])
                            )
                        speakerscores.append((ss_obj, bs_obj))

        BallotSubmission.objects.bulk_create(ballotsubmissions)

        DebateTeamMotionPreference.objects.bulk_create(self._add_foreign_key(motion_vetos_bs, 'ballot_submission'))
        TeamScore.objects.bulk_create(self._add_foreign_key(teamscores, 'ballot_submission'))
        SpeakerScore.objects.bulk_create(self._add_foreign_key(speakerscores, 'ballot_submission'))
        SpeakerScoreByAdj.objects.bulk_create(self._add_foreign_key(speakerscores_adj, 'ballot_submission'))

    def import_feedback(self):
        for adj in self.root.findall('participants/adjudicator'):
            adj_obj = self.adjudicators[adj.get('id')]

            for feedback in adj.findall('feedback'):
                d_adj = self.debateadjudicators.get((feedback.get('debate'), feedback.get('source-adjudicator')))
                d_team = self.debateteams.get((feedback.get('debate'), feedback.get('source-team')))
                feedback_obj = AdjudicatorFeedback(adjudicator=adj_obj, score=feedback.get('score'), version=1,
                    source_adjudicator=d_adj, source_team=d_team,
                    submitter_type=Submission.SUBMITTER_TABROOM, confirmed=True)
                feedback_obj.save()

                for answer in feedback.findall('answer'):
                    question = self.questions[answer.get('question')]

                    cast_answer = answer.text
                    # if question.answer_type in AdjudicatorFeedbackQuestion.NUMERICAL_ANSWER_TYPES:
                    #     cast_answer = float(cast_answer)

                    answer = AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[question.answer_type](
                        question=question, answer=cast_answer, feedback=feedback_obj)
