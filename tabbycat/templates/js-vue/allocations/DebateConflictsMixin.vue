<script>
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  mixins: [ConflictUtilitiesMixin],
  data: function () {
    return {
      debugMode: true
    }
  },
  watch: {
    filteredPanelConflicts: function() {
      // Re-up all conflicts when the master conflicts dictionary changes
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
      // conflicts
      this.activatePanelConflicts()
    })
  },
  computed: {
    allPanelConflicts: function() {
      // An array of conflicts gathered from each team or adjudicator
      var debateAdjs = _.map(this.panelAdjudicators, function(da) {
        return da.adjudicator
      })
      var debateTeams = _.map(this.panelTeams, function(dt) {
        return dt.team
      })
      var allTeamsAndAdjs = debateAdjs.concat(debateTeams)
      var allConflicts = _.mapValues(allTeamsAndAdjs, function(conflictable) {
        return conflictable.conflicts;
      });
      return allConflicts
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
      console.log('deactivatePanelConflicts')
      var self = this
      _.forEach(this.adjudicatorIds, function(id, dt) {
        self.unsendConflict(id, 'adjudicator', 'panel')
      })
      _.forEach(this.teamIds, function(id, da) {
        self.unsendConflict(id, 'team', 'panel')
      })
    },
    activatePanelConflicts: function() {
      // Turn on all conflicts as set by the filteredPanelConflicts()
      console.log('activatePanelConflicts')
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
        return this.checkIfInPanelWithInstitution(conflict.id)
      } else if (type === 'team' && _.includes(this.teamIds, conflict.id)) {
        return true // Team not present
      } else if (type === 'adjudicator' && _.includes(this.adjudicatorIds, conflict.id)) {
        return true // Adj not present
      }
      return false
    },
    checkIfInPanelWithInstitution: function(conflict) {
      return false
      // var self = this
      // _.forEach(this.panelTeams, function(dt) {
      //   var team = dt.team
      //   if ( (team.institution.id === conflict && team !== conflictingItem) &&
      //        (_.has(conflictingItem, 'score')) ) {
      //     // Don't self-conflict and don't allow team-team institution conflicts
      //     var eventCode = 'set-conflicts-for-team-' + team.id
      //     self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
      //     // Reverse the conflict (incase conflicting not own institution)
      //     var eventCode = 'set-conflicts-for-adjudicator-' + conflictingItem.id
      //     self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
      //   }
      // })
      // _.forEach(this.panelAdjudicators, function(panellist) {
      //   var adj = panellist.adjudicator
      //   if (adj.institution.id === conflict && adj !== conflictingItem) {
      //     var eventCode = 'set-conflicts-for-adjudicator-' + adj.id
      //     self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
      //     // Reverse the conflict (incase conflicting not own institution)
      //     var eventCode = 'set-conflicts-for-adjudicator-' + conflictingItem.id
      //     self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
      //   }
      // })
    }
  },
}
</script>
