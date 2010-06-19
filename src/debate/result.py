# cannot import debate.models here - would create circular dep

class Scoresheet(object):
    """
    Representation of an adjudicator's scoresheet

    self.data is a nested dictionary, such that
    self.data[side][pos] = score
    """

    def __init__(self, debate, adjudicator):
        self.debate = debate
        self.adjudicator = adjudicator

        from debate import models as m

        self.da = m.DebateAdjudicator.objects.get(
            adjudicator = self.adjudicator,
            debate = self.debate,
        )

        self.data = {
            'aff': self._no_scores(),
            'neg': self._no_scores()
        }

        self._init_side('aff')
        self._init_side('neg')

    def _no_scores(self):
        return dict((i, None) for i in range(1, 5))

    def _init_side(self, side):
        """
        Load from database
        """

        from debate import models as m

        dt = self.debate.get_dt(side)

        scores = m.SpeakerScoreByAdj.objects.filter(
            debate_adjudicator = self.da,
            debate_team = dt,
        )

        for ss in scores:
            self.set_score(side, ss.position, ss.score)

    def save(self):

        from debate import models as m

        # delete existing db objects
        m.SpeakerScoreByAdj.objects.filter(
            debate_adjudicator = self.da,
        ).delete()

        self._save_side('aff')
        self._save_side('neg')

    def _save_side(self, side):
        """
        Save to database
        """

        from debate import models as m

        dt = self.debate.get_dt(side)

        # create new ones
        for pos in range(1, 5):
            m.SpeakerScoreByAdj(
                debate_adjudicator = self.da,
                debate_team = dt,
                position = pos,
                score = self.get_score(side, pos),
            ).save()


    def set_score(self, side, position, score):
        self.data[side][position] = score

    def get_score(self, side, position):
        return self.data[side][position]

    @property
    def aff_score(self):
        return self.get_total('aff')

    @property
    def neg_score(self):
        return self.get_total('neg')

    def get_total(self, side):
        """
        Return total score for side
        """
        scores = [self.data[side][p] for p in range(1, 5)]
        if None in scores:
            return 0
        return sum(scores)


class DebateResult(object):
    """
    Encapsulates the result of a debate

    This class makes it easier for views & forms to work with the result
    of a debate. 

    It acts as a translation layer on top of the following db models:


    SpeakerScoreSheet
    TeamScore
    SpeakerScore

    """

    def __init__(self, debate):
        self.debate = debate
        self.adjudicators = debate.adjudicators.list
        self.adjudicator_sheets = dict(
            (a, Scoresheet(self.debate, a)) for a in self.adjudicators
        )

        self.speakers = {
            'aff': {},
            'neg': {},
        }

        self.points = {
            'aff': None,
            'neg': None,
        }

        self._other = {
            'aff': 'neg',
            'neg': 'aff',
        }

        self._calc_decision()
        self._init_side('aff')
        self._init_side('neg')

    def _init_side(self, side):
        dt = self.debate.get_dt(side)
        from debate.models import SpeakerScore, TeamScore

        for sss in SpeakerScore.objects.filter(
            debate_team = dt,
        ):

            self.speakers[side][sss.position] = sss.speaker
            
        try:
            ts = TeamScore.objects.get(debate_team=dt)
            points = ts.points
        except TeamScore.DoesNotExist:
            points = None


        self.points[side] = points

    def save(self):
        for sheet in self.adjudicator_sheets.values():
            sheet.save()

        self._calc_decision()

        self._save('aff')
        self._save('neg')

    def _calc_decision(self):
        decision = []
        for adj in self.adjudicators:
            aff_score = self.adjudicator_sheets[adj].aff_score
            neg_score = self.adjudicator_sheets[adj].neg_score
            decision.append((adj, aff_score > neg_score))

        votes = [v for a, v in decision]
        majority_aff = votes.count(True) > votes.count(False)
        self.majority_adj = [a for a, v in decision if v == majority_aff]


    def _save(self, side):
        from debate.models import TeamScore, SpeakerScore

        dt = self.debate.get_dt(side)
        total = self._score(side)
        points = self._points(side)

        TeamScore.objects.filter(debate_team=dt).delete()
        TeamScore(debate_team=dt, score=total, points=points).save()

        SpeakerScore.objects.filter(debate_team=dt).delete()
        for i in range(1, 5):
            speaker = self.speakers[side][i]
            score = self.get_avg_score(side, i)
            SpeakerScore(
                debate_team = dt,
                speaker = speaker,
                score = score,
                position = i,
            ).save()

        
    def get_speaker(self, side, position):
        """
        Return the speaker object for side/position
        """
        return self.speakers[side][position]

    def get_score(self, adj, side, position):
        """
        Return the score for the speaker in side/position
        """
        return self.adjudicator_sheets[adj].get_score(side, position)

    def get_avg_score(self, side, position):
        """
        Return the average score of majority adjudicators for side/position
        """
        return sum(self.adjudicator_sheets[adj].get_score(side, position)
                   for adj in self.majority_adj) / len(self.majority_adj)

    def get_speaker_score(self, adj, side, position):
        return (self.get_speaker(side, position), self.get_score(side, position))

    def set_speaker(self, side, pos, speaker):
        self.speakers[side][pos] = speaker

    def set_score(self, adj, side, position, score):
        """
        Set the score given by adj for side/position
        """
        self.adjudicator_sheets[adj].set_score(side, position, score)


    def _score(self, side):
        return sum(self.adjudicator_sheets[adj].get_total(side) for adj in
                   self.majority_adj) / len(self.majority_adj)

    @property
    def aff_score(self):
        return self._score('aff')

    @property
    def neg_score(self):
        return self._score('neg')

    def _points(self, side):
        if self._score(side):
            if self._score(side) > self._score(self._other[side]):
                return 1
            return 0
        return None

    @property
    def aff_points(self):
        return self._points('aff')

    @property
    def neg_points(self):
        return self._points('neg')

    @property
    def aff_win(self):
        return self.aff_points

    @property
    def neg_win(self):
        return self.neg_points


