<script>
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  mixins: [ConflictUtilitiesMixin],
  data: function () { return { debugMode: false }},
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
      return _.map(this.panelTeams, function(dt) { return dt.team })
    },
    adjudicators: function() {
      return _.map(this.panelAdjudicators, function(da) { return da.adjudicator })
    },
    allPanelConflicts: function() {
      // Create an array of conflicts gathered from each team or adjudicator
      var allConflicts = _.map(this.adjudicators, function(adj) {
        return adj.conflicts
      })
      _.forEach(this.teams, function(team) {
        // Remove any institutional conflicts coming from teams; only via adjs
        delete team.conflicts.clashes.institution
        allConflicts.push(team.conflicts)
      })
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
      var self = this
      _.forEach(this.adjudicatorIds, function(id, da) {
        self.unsendConflict(id, 'adjudicator', 'adjudicator', 'panel', 'clashes')
        self.unsendConflict(id, 'adjudicator', 'adjudicator', 'panel', 'histories')
        self.unsendConflict(id, 'institution', 'adjudicator', 'panel', 'clashes')
      })
      _.forEach(this.teamIds, function(id, dt) {
        self.unsendConflict(id, 'team', 'team', 'panel', 'clashes')
        self.unsendConflict(id, 'team', 'team', 'panel', 'histories')
        self.unsendConflict(id, 'institution', 'team', 'panel', 'clashes')
      })
    },
    activatePanelConflicts: function() {
      // Turn on all conflicts as set by the filteredPanelConflicts()
      var self = this
      this.forEachConflict(this.filteredPanelConflicts,
        function(conflict, type, clashOrHistory) {
          if (type === 'institution') {
            self.activatePanelWithInstitutionalConflict(conflict)
          } else {
            self.sendConflict(conflict, type, type, 'panel', clashOrHistory)
          }
        }
      )
    },
    activatePanelWithInstitutionalConflict: function(conflict) {
      // For institutional conflicts within a panel we want to send them
      // out in a targetted fashion (unlike for say hover-overs where we
      // can do a global broadcast by institutional ID); that is to say we
      // need to find and target just the teams/adjs who need them and then
      // target those items specifically

      var teamsMatches = _.filter(this.teams, function(team) {
        return team.institution.id === conflict.id;
      });

      _.forEach(this.teamsMatches, function(team) {
        if (team.institution.id === conflict.id) {
          console.log('team match')
          self.sendConflict(team.id, 'team', 'institutional', 'panel', 'clashes')
        }
      })

      var adjsMatches = _.filter(this.adjudicators, function(adj) {
        return adj.institution.id === conflict.id;
      });

      // _.forEach(this.adjudicators, function(adjudicator) {
      //   if (adjudicator.institution.id === conflict.id) {
      //     console.log('team match')
      //     //self.sendConflict(team.id, 'team', 'institutional', 'panel', 'clashes')
      //   }
      // })


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
