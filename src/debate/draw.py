import random
from debate.utils import pair_list, memoize

class DrawError(Exception):
    pass

class BaseDraw(object):
    def __init__(self, round):
        from debate.models import TeamAtRound

        self.round = round
        if not self.round.draw_status == self.round.STATUS_NONE:
            raise DrawError()
        from django.db.models import Sum
        teams = self.round.active_teams.annotate(
            points = Sum('debateteam__teamscore__points'),
            speaker_score = Sum('debateteam__teamscore__score')
        ).order_by('-points', '-speaker_score')
        self.teams = [TeamAtRound(team, round.prev) for team in teams]
        
        if not len(self.teams) % 2 == 0:
            raise DrawError()
        
    def balance_sides(self, pairs):
        p = []
        for pair in pairs:
            if pair[0].aff_count < pair[1].aff_count:
                p.append((pair[0], pair[1]))
            elif pair[0].aff_count > pair[1].aff_count:
                p.append((pair[1], pair[0]))
            else:
                l = list(pair)
                random.shuffle(l)
                p.append(l)
        return p

    def draw(self):
        return self.get_draw()

        
class RandomDraw(BaseDraw):
    def get_draw(self):
        random.shuffle(self.teams)
        return pair_list(self.teams)

class RandomDrawNoConflict(RandomDraw):
    MAX_SWAP_ATTEMPTS = 10

    def get_draw(self):
        draw = super(RandomDrawNoConflict, self).get_draw()

        for i, (aff, neg) in enumerate(draw):
            if aff.institution == neg.institution:
                for j in range(self.MAX_SWAP_ATTEMPTS):
                    k = random.randint(0, len(draw)-1)
                    n_aff, n_neg = draw[k]
                    if (n_aff.institution != aff.institution and
                        n_neg.institution != aff.institution):
                        m1 = (aff, n_neg)
                        m2 = (n_aff, neg)
                        draw[i] = m1
                        draw[k] = m2
                        break
        return draw
     
class AidaDraw(BaseDraw):
    
                
    def get_draw(self):
        from debate.aida import one_up_down

        pools = self.make_pools()
        pairs = []
        
        for pool in pools:
            debates = len(pool) / 2
            top = pool[:debates]
            bottom = pool[debates:]

            pool_draw = zip(top, bottom)
            one_up_down(pool_draw)
            
            pairs.extend(pool_draw)
        return self.balance_sides(pairs)                
                    
        
    def make_pools(self):
        pools = []
        teams = list(self.teams)
        
        while len(teams) > 0:
            top_team = teams.pop(0)
            pool = []
            pool.append(top_team)
            while len(teams) > 0 and teams[0].points == top_team.points:
                pool.append(teams.pop(0))
            if len(pool) % 2 != 0:
                pool.append(teams.pop(0))
            pools.append(pool)
        return pools
        
class BracketDraw(BaseDraw):
    def get_draw(self):
        teams = self.teams
        max_points = teams[0].total_points
        brackets = ([],) * (max_points + 1)
        for team in teams:
            brackets[team.total_points].append(team)
        # balance brackets from top down
        for i in range(max_points, -1, -1):
            if len(brackets[i]) % 2 != 0:
                # find next non-empty bracket
                idx = i - 1
                while len(brackets[idx]) == 0:
                    idx -= 1
                brackets[i].append(brackets[idx].pop(0))
        # construct pairs by folding non-empty brackets
        pairs = []
        for bracket in brackets:
            num = len(bracket)
            for i in range(num/2):
                pairs.append(bracket[i], bracket[num+i])
        return pairs

def assign_importance(round):
    debates = round.get_draw().order_by('-bracket')
    adjudicators = list(round.active_adjudicators.all())
    adjudicators.sort(key=lambda a:-a.score)

    bs = round.tournament.config.get('break_size')

    bubble_bracket = debates[(bs/2)-1].bracket

    # TODO: impl round specific
    nd = float(len(debates))
    na = len(adjudicators)

    for i, debate in enumerate(debates):
        debate.importance = adjudicators[int(i*na/nd)].score

        debate.save()


    

    


