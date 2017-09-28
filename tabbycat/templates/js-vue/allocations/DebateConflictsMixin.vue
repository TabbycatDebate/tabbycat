<script>
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  mixins: [ConflictUtilitiesMixin],
  data: function () {
    return { debugMode: false }
  },
  watch: {
    filteredConflicts: function() {
      // Re-calculate all conflicts when the master conflicts dictionary changes
      this.$nextTick(function() {
        // MUST wait for all data to finish resolving when panel info has been
        // updated before recalculating conflicts
        this.deactivatePanelConflicts()
        this.activatePanelConflicts()
      })
    }
  },
  mounted: function() {
    this.$nextTick(function() {
      // MUST to wait for DOM to resolve on initial load before calculating
      // the conflicts
      this.activatePanelConflicts()
    })
  },
  computed: {
    teams: function() {
      return _.map(this.panelTeams, function(dt) { return dt.team })
    },
    adjudicators: function() {
      return _.map(this.panelAdjudicators, function(da) { return da.adjudicator })
    },
    allConflicts: function() {
      // Create an array of conflicts gathered from each team or adjudicator
      var allConflicts = _.map(this.adjudicators, function(adj) {
        return adj.conflicts
      })
      _.forEach(this.teams, function(team) {
        // Remove any institutional conflicts coming from teams; only via adjs
        var teamConflicts = _.clone(team.conflicts)
        delete teamConflicts.clashes.institution
        if (!_.isEmpty(teamConflicts)) {
          allConflicts.push(teamConflicts)
        }
      })
      return allConflicts
    },
    filteredConflicts: function() {
      // Traverse the combined conflicts object and delete those not relevant
      // to the panel. This allows us to (later) activate all the leftovers
      var subset = {
        'clashes': { 'adjudicator': [], 'institution': [], 'team': [] },
        'histories': { 'adjudicator': [], 'institution': [], 'team': [] }
      }
      var self = this
      _.forEach(this.allConflicts, function(adjOrTeamsConflicts) {
        // For all of the panel conflicts
        self.forEachConflict(adjOrTeamsConflicts, function(conflict, type, clashOrHistory) {
          // Drill down into each adj/teams conflicts and filter out those
          // that cannot apply to the panel as-is
          if (self.checkIfInPanel(conflict, type, clashOrHistory)) {
            subset[clashOrHistory][type].push(conflict)
          }
        })
      })
      // De-duplicate the institutional IDs; often they are multiple overlaps
      subset['clashes']['institution'] = _.uniqBy(subset['clashes']['institution'], 'id')
      return subset
    },
  },
  methods: {
    deactivatePanelConflicts: function() {
      // Turn off all conflicts that might remain from previous panellists who
      // have been moved on
      var self = this
      if (this.debugMode) {
        console.log('Deactivate panel conflicts for', this.debateId);
      }
      _.forEach(this.adjudicatorIds, function(id, da) {
        self.unsendConflict({ id: id }, 'adjudicator', 'adjudicator', 'panel', 'clashes')
        self.unsendConflict({ id: id }, 'adjudicator', 'adjudicator', 'panel', 'histories')
        self.unsendConflict({ id: id }, 'institution', 'adjudicator', 'panel', 'clashes')
      })
      _.forEach(this.teamIds, function(id, dt) {
        self.unsendConflict({ id: id }, 'team', 'team', 'panel', 'clashes')
        self.unsendConflict({ id: id }, 'team', 'team', 'panel', 'histories')
        self.unsendConflict({ id: id }, 'institution', 'team', 'panel', 'clashes')
      })
    },
    activatePanelConflicts: function() {
      // Turn on all conflicts by activating what hs been set by
      // filteredPanelConflicts(). Calls/happens when a panel updates
      var self = this
      if (this.debugMode) {
        console.log('Activate panel conflicts for', this.debateId);
      }
      this.forEachConflict(this.filteredConflicts, function(conflict, type, clashOrHistory) {
        if (type === 'institution') {
          self.activatePanelWithInstitutionalConflict(conflict) // See below
        } else {
          self.sendConflict(conflict, type, type, 'panel', clashOrHistory)
        }
      })
    },
    activatePanelWithInstitutionalConflict: function(conflict) {
      // For institutional conflicts within a panel we want to send them
      // out in a targetted fashion (unlike for say hover-overs where we
      // can do a global broadcast by institutional ID); that is to say we
      // need to find and target just the teams/adjs who need them and then
      // target those items specifically
      var self = this

      var teamsMatches = _.filter(this.teams, function(team) {
        if (team.institution !== null) {
          return team.institution.id === conflict.id;
        }
      });
      // Find teams of the same institution as the conflict
      _.forEach(teamsMatches, function(team) {
        if (team.institution.id === conflict.id) {
          self.sendConflict(team, 'team',       'institution', 'panel', 'clashes')
        }
      })

      // Find adjs who have the same institutional conflicts as the conflict we
      // we are checking. We have to loop over the adj in questions actual
      // institutional conflicts; not just their current institution as
      // its a many to many relationship
      var adjsMatches = _.filter(this.adjudicators, function(adj) {
        var adjudicatorsInstitutions = adj.conflicts.clashes.institution
        var institutionIDs = _.map(adjudicatorsInstitutions, 'id');
        if (institutionIDs.indexOf(conflict.id) !== -1) {
          return true
        } else {
          return false
        }
      });

      // Unlike with teams; adj-adj institution conflicts require co-presence
      if (adjsMatches.length > 1 || teamsMatches.length > 0) {
        _.forEach(adjsMatches, function(adj) {
          self.sendConflict(adj, 'adjudicator', 'institution', 'panel', 'clashes')
        })
      }
    },
    checkIfInPanel: function(conflict, type, clashOrHistory) {
      // For a given conflict from a team/adj check if it can actually apply
      // to the panel
      if (type === 'institution') {
        return true // These are calculated later
      } else if (type === 'team' && _.includes(this.teamIds, conflict.id)) {
        return true // Team not present
      } else if (type === 'adjudicator' && _.includes(this.adjudicatorIds, conflict.id)) {
        return true // Adj not present
      }
      return false
    },
  },
}
</script>
