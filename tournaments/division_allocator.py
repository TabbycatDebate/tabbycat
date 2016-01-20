from tournaments.models import Division
import random

class DivisionAllocator():

    def __init__(self, teams, divisions, venue_groups, tournament, institutions):
        print("Allocating divisions for %s" % tournament)
        self.teams = teams
        self.divisions = divisions
        self.venue_groups = venue_groups
        self.tournament = tournament
        self.institutions = institutions
        self.minimum_division_size = tournament.pref('minimum_division_size')# cannot see teams more than once
        self.ideal_division_size = tournament.pref('ideal_division_size')
        self.maximum_division_size = tournament.pref('maximum_division_size') # shouldn't have more than two byes?


    def allocate(self):
        # Entry Point
        division_dict = {v:[] for v in self.venue_groups}
        allocated_teams = []
        all_preferences = []
        all_teams = self.teams

        # Get all the relevant team preferences
        for team in all_teams:
            if team.venue_preferences:
                all_preferences.extend(team.venue_preferences)

        # Get all the relevant institution preferences
        all_institutions = self.institutions
        for institution in all_institutions:
            if institution.venue_preferences:
                all_preferences.extend(institution.venue_preferences)


        # First sweep of allocations using team preferences
        division_dict, allocated_teams = self.allocate_teams(division_dict, allocated_teams, all_teams, all_preferences)
        print("Post-Allocate 1: have %s/%s teams allocated across %s venues" % (len(allocated_teams), len(all_teams), len(division_dict)))

        # # First round of culls
        # division_dict, allocated_teams = self.cull_venues(division_dict, allocated_teams)
        # print("Post-Cull 1: have %s/%s teams allocated across %s venues" % (len(allocated_teams), len(all_teams), len(division_dict)))

        # # Second sweep of allocations
        # unalloacted_teams = [te for te in all_teams if not te in allocated_teams]
        # division_dict, allocated_teams = self.allocate_teams(division_dict, allocated_teams, unalloacted_teams, )
        # print("Post-Allocate 2: have %s/%s teams allocated across %s venues" % (len(allocated_teams), len(all_teams), len(division_dict)))

        self.determine_division_size(division_dict, allocated_teams,all_teams)

        return True


    def allocate_teams(self, division_dict, allocated_teams, all_teams, all_preferences):
        teams_to_allocate = list(all_teams)
        random.shuffle(all_teams)
        random.shuffle(all_preferences)
        all_preferences.sort(key=lambda x: x.priority, reverse=True)
        # Division dictionary structure: { <VenueGroup: PC Wed W1>: [], <VenueGroup: PC Wed W2>: [], ... }

        # Sort preferences by priority then do all the allocations
        for preference in all_preferences:
            if len(division_dict[preference.venue_group]) >= preference.venue_group.team_capacity:
                # If this venue is full
                pass
            elif hasattr(preference, 'team'):
                if preference.team not in allocated_teams:
                    print("allocating team %s to venue group %s (%s/%s) based on team priority of %s" % (
                        preference.team, preference.venue_group, len(division_dict[preference.venue_group]), preference.venue_group.team_capacity, preference.priority))
                    group = preference.venue_group
                    division_dict[group].append(preference.team)
                    allocated_teams.append(preference.team)
                    teams_to_allocate.remove(preference.team)
            elif hasattr(preference, 'institution'):
                for team in teams_to_allocate:
                    if team.institution == preference.institution and team not in allocated_teams:
                        print("allocating team %s to venue group %s (%s/%s) based on institutional priority of %s" % (
                            team, preference.venue_group, len(division_dict[preference.venue_group]), preference.venue_group.team_capacity, preference.priority))
                        group = preference.venue_group
                        division_dict[group].append(team)
                        allocated_teams.append(team)
                        teams_to_allocate.remove(team)

        # Randomly apply leftovers
        for team in teams_to_allocate:
            venues_with_capacity = [v for v in list(division_dict.keys()) if len(division_dict[v]) <= v.team_capacity - 1]
            random_veunue = random.choice(venues_with_capacity)
            if random_veunue:
                print("allocating team %s to venue group %s (%s/%s) based on last resort" % (
                    team, random_veunue, len(division_dict[random_veunue]), random_veunue.team_capacity))
                division_dict[random_veunue].append(team)
                allocated_teams.append(team)

        for group, group_teams in division_dict.items():
            # Trying to mix up the distributions within divisions
            random.shuffle(group_teams)
            random.shuffle(group_teams)
            random.shuffle(group_teams)

        return division_dict, allocated_teams

    def cull_venues(self, division_dict, allocated_teams):

        culled_division_dict = {}
        for group, group_teams in division_dict.items():
            if len(group_teams) > 0 and len(group_teams) < self.minimum_division_size:
                # If the amount of allocated teams is not enough for one division
                print("\t culling %s because too few teams (%s)" % (group, len(group_teams)))
                for ttr in group_teams:
                    allocated_teams.remove(ttr)
            else:
                culled_division_dict[group] = group_teams

        return culled_division_dict, allocated_teams

    def determine_division_size(self,division_dict, allocated_teams,all_teams):
        di = 1 # index of current division

        for group,group_teams in division_dict.items():
            if len(group_teams) > 0:
                print("------\n%s has %s/%s teams" % (group, len(group_teams), group.team_capacity))

                # Using the ideal division size, how many divisions can we support?
                possible_ideal_divisions = len(group_teams) // self.ideal_division_size
                possible_ideal_remainder = len(group_teams) % self.ideal_division_size
                print("\t %s possible_ideal_division of 6 with %s leftover" % (possible_ideal_divisions, possible_ideal_remainder))
                possible_small_divisions = len(group_teams) // self.minimum_division_size
                possible_small_remainder = len(group_teams) % self.minimum_division_size
                print("\t %s possible_small_division of 5 with %s leftover" % (possible_small_divisions, possible_small_remainder))

                if min(possible_ideal_remainder, possible_small_remainder) == possible_ideal_remainder and possible_ideal_divisions > 0:
                    di = self.create_venue_divisions(group,group_teams,di,self.ideal_division_size,possible_ideal_divisions,possible_ideal_remainder)
                elif min(possible_ideal_remainder, possible_small_remainder) == possible_small_remainder and possible_small_divisions > 0:
                    di = self.create_venue_divisions(group,group_teams,di,self.minimum_division_size,possible_small_divisions,possible_small_remainder)
                else:
                    print("\t no options - this shouldn't happen")

        print("------")
        print("Made %s divisions over %s venues, Allocated %s / %s teams" % (di, len(division_dict), len(allocated_teams), len(all_teams)))

        unalloacted_teams = [te for te in all_teams if not te in allocated_teams]
        for ute in unalloacted_teams:
            # print("\t %s not allocated" % ute)
            pass


    def create_division(self, di, group, group_teams, team_index, division_size):

        new_division, created = Division.objects.get_or_create(
            name = str(di),
            tournament = self.tournament,
            venue_group = group
        )
        for i in range(team_index,team_index+division_size):
            group_teams[i].division = new_division
            group_teams[i].save()

        print("\t Made division #%s of size %s" % (new_division, division_size))


    def create_venue_divisions(self,group,group_teams,di,base_division_size,possible_divisions,remainder):

        random.shuffle(group_teams)
        divisions = [base_division_size] * possible_divisions

        for i in range(0, remainder):
            # Re-distributing the excess numbers to the other divisions
            divisions.sort()
            divisions[0] += 1

        team_index = 0
        for division_size in divisions:
            self.create_division(di,group,group_teams,team_index,division_size)
            team_index += division_size
            di += 1

        return di
