from xml.etree.ElementTree import Element, SubElement

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, Q

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedbackQuestion
from draw.models import Debate
from motions.models import Motion
from participants.models import Institution, Speaker
from results.models import BallotSubmission
from results.prefetch import populate_confirmed_ballots, populate_wins
from results.result import (BaseConsensusDebateResultWithSpeakers, BaseDebateResultWithSpeakers,
                            BaseEliminationDebateResult, DebateResult, VotingDebateResult)
from tournaments.models import Round


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
        self.root = Element('tournament', {'name': tournament.name})

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
        debate_prefetch = Prefetch('debate_set', queryset=Debate.objects.all().prefetch_related(
            'debateteam_set', 'debateteam_set__team', 'debateteam_set__team__institution', 'debateadjudicator_set', results_prefetch))

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
                    speaker_tag.set('institution', INST_PREFIX + str(team.institution_id))

                if speaker.gender != "":
                    speaker_tag.set('gender', speaker.get_gender_display())

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
                adj_tag.set('institution', INST_PREFIX + str(adj.institution_id))

            if adj.gender != "":
                adj_tag.set('gender', adj.get_gender_display())

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
