import random
from debate.utils import pair_list

class DrawError(Exception):
    pass
    
class BaseDraw(object):
    def __init__(self, round):
        self.round = round
        if not self.round.draw_status == self.round.STATUS_NONE:
            raise DrawError()
        self.teams = list(self.round.active_teams.all())
        
        if not len(self.teams) % 2 == 0:
            raise DrawError()
        
    def balance_sides(self, pairs):
        p = []
        for pair in pairs:
            if pair[0].aff_count < pair[0].neg_count:
                p.append(pair[0], pair[1])
            elif pair[0].aff_count > pair[0].neg_count:
                p.append(pair[1], pair[0])
            else:
                l = list(pair)
                random.shuffle(l)
                p.append(l)
        return p
        
class RandomDraw(BaseDraw):
    def get_draw(self):
        random.shuffle(self.teams)
        return pair_list(self.teams)
     
class AidaDraw(BaseDraw):
    
                
    def get_draw(self):
        pools = self.make_pools()
        pairs = []
        
        for pool in pools:
            debates = len(pool) / 2
            top = pool[:debates]
            bottom = pool[debates:]
            
            def one_up(idx):
                # do the swap if it doesn't result in a repeat matchup
                if not top[i].seen(bottom[i+1]) and not top[i+1].seen(bottom[i]):
                    swap(idx)
                    return True
                return False
            def one_down(idx):
                # do the swap if it doesn't result in a repeat matchup
                if not top[i].seen(bottom[i-1]) and not top[i-1].seen(bottom[i]):
                    swap(idx-1)
                    return True
                return False
            
            def swap(idx):
                # perform swap with idx and idx+1
                # all swaps are done in the bottom pool
                tmp = bottom[idx]
                bottom[idx] = bottom[idx+1]
                bottom[idx+1] = tmp                
            
            for i in range(debates):
                if top[i].seen(bottom[i]) or top[i].same_institution(bottom[i]):
                    if i == 0:
                        one_down(i)
                    elif i == debates - 1:
                        one_up(i)
                    else:
                        if not one_up(i):
                            one_down(i)
            pairs.extend(zip(top, bottom))
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
