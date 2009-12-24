from debate.models import Venue, Institution, Adjudicator, Team, AdjudicatorConflict, Speaker, Round

class Importer(object):
    institutions = {}
    adjudicators = {}
    teams = {}
    venues = {}
    speakers = {}

    def import_institutions(self, fname):
        for line in open(fname):
            id, code, name, c, u = line.split('\t')
            i = Institution(code=code.strip(), name=name.strip())
            i.save()
            self.institutions[int(id)] = i

    def import_adjudicators(self, fname):
        for line in open(fname):
            id, name, test_score, institution_id, active, c, u = line.split('\t')
            a = Adjudicator(name=name.strip(),
                            institution=self.institutions[int(institution_id)],
                            test_score = float(test_score))
            a.save()
            self.adjudicators[int(id)] = a

    def import_venues(self, fname):
        for line in open(fname):
            id, name, active, priority, c, u = line.split('\t')
            v = Venue(name=name.strip(), priority=int(priority))
            v.save()
            self.venues[int(id)] = v

    def import_teams(self, fname):
        for line in open(fname):
            id, name, institution_id, swing, active, c, u = line.split('\t')
            t = Team(name=name.strip(), 
                     institution=self.institutions[int(institution_id)])
            t.save()
            self.teams[int(id)] = t

    def import_speakers(self, fname):
        for line in open(fname):
            id, name, team_id, c, u = line.split('\t')
            s = Speaker(name=name.strip(),
                        team=self.teams[int(team_id)])
            s.save()
            self.speakers[int(id)] = s

    def import_adjudicator_conflicts(self, fname):
        for line in open(fname):
            id, team_id, adjudicator_id, c, u = line.split('\t')
            c = AdjudicatorConflict(team=self.teams[int(team_id)],
                                    adjudicator=self.adjudicators[int(adjudicator_id)])
            c.save()

            


def run():
    im = Importer()
    im.import_institutions('institutions.tab')
    im.import_adjudicators('adjudicators.tab')
    im.import_venues('venues.tab')
    im.import_teams('teams.tab')
    im.import_speakers('speakers.tab')
    im.import_adjudicator_conflicts('adjudicator_conflicts.tab')


    r = Round(seq=1, type=Round.TYPE_RANDOM)
    r.save()
    r.activate_all()




if __name__ == '__main__':
    run()
