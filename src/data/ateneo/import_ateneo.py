import debate.models as m


class Importer(object):
    def __init__(self, tournament, fname):
        self.fname = fname

        self.tournament = tournament
        self.institutions = {}
        self.adjudicators = {}
        self.teams = {}
        self.venues = {}
        self.speakers = {}
        self.rounds = {}
        self.debates = {}
        self.debate_teams = {}
        self.adjudicator_allocations = {}
        self.speaker_score_sheets = {}
        self.team_score_sheets = {}

    def import_institutions(self):
        for line in self.load_table('institutions'):
            id, code, name, c, u = line.split('\t')
            i = m.Institution(code=code.strip(), name=name.strip(),
                             tournament=self.tournament)
            i.save()
            self.institutions[int(id)] = i

    def import_adjudicators(self):
        for line in self.load_table('adjudicators'):
            id, name, test_score, institution_id, active, c, u = line.split('\t')
            a = m.Adjudicator(name=name.strip(),
                            institution=self.institutions[int(institution_id)],
                            test_score = float(test_score),
                             cv_score = float(test_score))
            a.save()
            self.adjudicators[int(id)] = a

    def import_venues(self):
        for line in self.load_table('venues'):
            id, name, active, priority, c, u = line.split('\t')
            v = m.Venue(tournament=self.tournament, name=name.strip(), priority=int(priority))
            v.save()
            self.venues[int(id)] = v

    def import_teams(self):
        for line in self.load_table('teams'):
            id, name, institution_id, swing, active, c, u = line.split('\t')
            t = m.Team(name=name.strip(), 
                     institution=self.institutions[int(institution_id)])
            t.save()
            self.teams[int(id)] = t

    def import_speakers(self):
        for line in self.load_table('debaters'):
            id, name, team_id, c, u = line.split('\t')
            s = m.Speaker(name=name.strip(),
                        team=self.teams[int(team_id)])
            s.save()
            self.speakers[int(id)] = s

    def import_adjudicator_conflicts(self):
        for line in self.load_table('adjudicator_conflicts'):
            id, team_id, adjudicator_id, c, u = line.split('\t')
            c = m.AdjudicatorConflict(team=self.teams[int(team_id)],
                                    adjudicator=self.adjudicators[int(adjudicator_id)])
            c.save()

    def load_table(self, table):
        in_table = False
        for line in open(self.fname):
            if in_table and line.startswith(r"\."):
                raise StopIteration
            if in_table:
                yield line
            if line.startswith("COPY %s " % table):
                in_table = True

    def load_round(self, rounds):
        _type = {
            '1': m.Round.TYPE_RANDOM,
            '2': m.Round.TYPE_PRELIM,
            '8': m.Round.TYPE_PRELIM,
            '4': m.Round.TYPE_BREAK,
        }

        for line in self.load_table('rounds'):
            id, name, type, status, pr, fw, c, u = line.split('\t')
            if int(id) in rounds:
                r = m.Round(
                    tournament = self.tournament,
                    seq = id,
                    name = name,
                    type = _type[type],
                    draw_status = m.Round.STATUS_CONFIRMED,
                    venue_status = m.Round.STATUS_CONFIRMED,
                    adjudicator_status = m.Round.STATUS_CONFIRMED,
                    feedback_weight = float(fw),
                )

                r.save()
                r.activate_all()
                self.rounds[int(id)] = r

        self.rounds[rounds[-1]].save()

        for line in self.load_table('debates'):
            id, round_id, venue_id, c, u = line.split('\t')
            if int(round_id) in rounds:
                d = m.Debate(
                    round = self.rounds[int(round_id)],
                    venue = self.venues[int(venue_id)],
                    result_status = m.Debate.STATUS_CONFIRMED,
                )
                d.save()
                self.debates[int(id)] = d

        _position = {
            '1': m.DebateTeam.POSITION_AFFIRMATIVE,
            '2': m.DebateTeam.POSITION_NEGATIVE,
        }

        for line in self.load_table('debates_teams_xrefs'):
            id, debate_id, team_id, pos, c, u = line.split('\t')

            if int(debate_id) in self.debates:

                d = m.DebateTeam(
                    debate = self.debates[int(debate_id)],
                    team = self.teams[int(team_id)],
                    position = _position[pos],
                )

                d.save()
                self.debate_teams[int(id)] = d

        _type = {
            '1': m.DebateAdjudicator.TYPE_CHAIR,
            '2': m.DebateAdjudicator.TYPE_PANEL,
        }

        for line in self.load_table('adjudicator_allocations'):
            id, debate_id, adj_id, type, c, u = line.split('\t')

            if int(debate_id) in self.debates:

                a = m.DebateAdjudicator(
                    debate = self.debates[int(debate_id)],
                    adjudicator = self.adjudicators[int(adj_id)],
                    type = _type[type],
                )
                a.save()
                self.adjudicator_allocations[int(id)] = a

        # read in speaker score sheets, then construct
        # actual scores later
        debates = {}
        P_AFF = m.DebateTeam.POSITION_AFFIRMATIVE
        P_NEG = m.DebateTeam.POSITION_NEGATIVE
        _side = {
            P_AFF: 'aff',
            P_NEG: 'neg',
        }
        for line in self.load_table('speaker_score_sheets'):
            id, aa_id, dt_id, s_id, score, pos, c, u = line.split('\t')

            if int(dt_id) in self.debate_teams:
                dt = self.debate_teams[int(dt_id)]
                d = dt.debate.id

                if d not in debates:
                    debates[d] = {}

                a = self.adjudicator_allocations[int(aa_id)].adjudicator.id

                if a not in debates[d]:
                    debates[d][a] = {
                        P_AFF: {},
                        P_NEG: {},
                    }


                speaker = self.speakers[int(s_id)]
                score = float(score)

                debates[d][a][dt.position][int(pos)] = (speaker, score)

        for debate_id, adjudicators in debates.items():

            dr = m.DebateResult(m.Debate.objects.get(pk=debate_id))
            for side in (P_AFF, P_NEG):
                for pos in range(1,5):
                    first_adj = adjudicators.values()[0]
                    speaker, _ = first_adj[side][pos]
                    dr.set_speaker(_side[side], pos, speaker)

                    for a_id in adjudicators:
                        adj = m.Adjudicator.objects.get(pk=a_id)
                        score = adjudicators[a_id][side][pos][1]
                        dr.set_score(adj, _side[side], pos, score)

            dr.save()

        for debate in m.Debate.objects.all():
            # set debate brackets
            if debate.round.prev is None:
                debate.bracket = 0
            else:
                aff_team = m.Team.objects.standings(
                    debate.round.prev).get(id=debate.aff_team.id)

                neg_team = m.Team.objects.standings(
                    debate.round.prev).get(id=debate.neg_team.id)

                debate.bracket = max(aff_team.points, neg_team.points)
            debate.save()

        def _int(id):
            if id.strip() == r'\N':
                return None
            return int(id)

        for line in self.load_table('adjudicator_feedback_sheets'):
            id, adj_id, aa_id, dt_id, comm, score, c, u = line.split('\t')
            dt_id = _int(dt_id)
            aa_id = _int(aa_id)

            if (dt_id in self.debate_teams 
                or aa_id in self.adjudicator_allocations):

                dt = self.debate_teams.get(dt_id)
                aa = self.adjudicator_allocations.get(aa_id)

                m.AdjudicatorFeedback(
                    adjudicator = self.adjudicators[int(adj_id)],
                    score = float(score),
                    comments = comm.strip(),
                    source_adjudicator = aa,
                    source_team = dt,
                ).save()

        self.tournament.current_round = m.Round.objects.order_by('-seq')[0]
        self.tournament.save()
 
def run():
    t = m.Tournament(slug='australs')
    t.save()
    im = Importer(t, 'stab_pt.sql')
    im.import_institutions()
    im.import_adjudicators()
    im.import_venues()
    im.import_teams()
    im.import_speakers()
    im.import_adjudicator_conflicts()

    return im

if __name__ == '__main__':
    im = run()
    import sys

    n_args = len(sys.argv)

    make_new = False

    if sys.argv[-1] == '--new':
        n_args -= 1
        make_new = True

    if n_args == 1:
        a, b = 1, 9
    elif n_args == 2:
        a, b = 1, int(sys.argv[1])
    else:
        a, b = int(sys.argv[1]), int(sys.argv[2])
    
    im.load_round(range(a, b))

    if make_new:
        im.tournament.create_next_round()

