<script>
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  mixins: [ConflictUtilitiesMixin],
  data: function () { return { debugMode: true }},
  watch: {
    filteredPanelConflicts: function() {
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
      return _.map(this.panelTeams, function(dt) {
        return dt.team
      })
    },
    adjudicators: function() {
      return _.map(this.panelAdjudicators, function(da) {
        return da.adjudicator
      })
    },
    allPanelConflicts: function() {
      // An array of conflicts gathered from each team or adjudicator
      var allTeamsAndAdjs = this.adjudicators.concat(this.teams)
      var allConflicts = _.mapValues(allTeamsAndAdjs, function(conflictable) {
        return conflictable.conflicts
      });
      return allConflicts
    },
    allInstitutionIDs: function() {
      var teamInstitutions = _.map(this.teams, 'institution.id')
      var adjInstitutions = _.map(this.adjudicators, 'institution.id')
      return teamInstitutions.concat(adjInstitutions)
    },
    filteredPanelConflicts: function() {
      // Traverse the combined conflicts object and delete those not relevant
      // to the panel
      var filteredConflicts = {
        'clashes': { 'adjudicator': [], 'institution': [], 'team': [] },
        'histories': { 'adjudicator': [], 'institution': [], 'team': [] }
      }
      var self = this
      _.forEach(this.allPanelConflicts, function(adjOrTeamsConflicts) {
        // For all of the panel conflicts
        self.forEachConflict(adjOrTeamsConflicts,
          function(conflict, type, clashOrHistory) {
            // Drill down into each adj/teams conflicts and filter out those
            // that cannot apply to the panel as-is
            if (self.checkIfInPanel(conflict, type, clashOrHistory)) {
              filteredConflicts[clashOrHistory][type].push(conflict)
            }
          }
        )
      })
      return filteredConflicts
    },
  },
  methods: {
    deactivatePanelConflicts: function() {
      // Turn off all conflicts that might remain from previous panellists
      var self = this
      _.forEach(this.adjudicatorIds, function(id, da) {
        self.unsendConflict(id, 'adjudicator', 'panel', 'clashes')
        self.unsendConflict(id, 'adjudicator', 'panel', 'histories')
      })
      _.forEach(this.teamIds, function(id, dt) {
        self.unsendConflict(id, 'team', 'panel', 'clashes')
        self.unsendConflict(id, 'team', 'panel', 'histories')
      })
      // For institutions just loop through unique instIDs present in the panel
      _.forEach(_.uniq(this.allInstitutionIDs), function(institutionId) {
        self.unsendConflict(institutionId, 'institution', 'panel', 'clashes')
      })
    },
    activatePanelConflicts: function() {
      // Turn on all conflicts as set by the filteredPanelConflicts()
      var self = this
      this.forEachConflict(this.filteredPanelConflicts,
        function(conflict, type, clashOrHistory) {
          self.sendConflict(conflict, type, 'panel', clashOrHistory)
        }
      )
    },
    checkIfInPanel: function(conflict, type, clashOrHistory) {
      // For a given conflict from a team/adj check if it can actually apply
      // to the panel
      if (type === 'institution') {
        return this.checkIfInPanelWithInstitution(conflict)
      } else if (type === 'team' && _.includes(this.teamIds, conflict.id)) {
        return true // Team not present
      } else if (type === 'adjudicator' && _.includes(this.adjudicatorIds, conflict.id)) {
        return true // Adj not present
      }
      return false
    },
    checkIfInPanelWithInstitution: function(conflict) {
      // Given a conflict with a certain institution we count up matching
      // teams/adjs and activate if there are more than 0 matches
      var teamsMatches = _.filter(this.panelTeams, function(debateTeam) {
        return debateTeam.team.institution.id === conflict.id;
      });
      var adjsMatches = _.filter(this.panelAdjudicators, function(panellist) {
        return panellist.adjudicator.institution.id === conflict.id;
      });
      if (teamsMatches.length + adjsMatches.length > 1) {
        return true
      } else {
        return false
      }
    }
  },
}
</script>
