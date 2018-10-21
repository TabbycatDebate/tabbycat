<script>
import _ from 'lodash'
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  mixins: [ConflictUtilitiesMixin],
  data: function () {
    return { debugMode: false }
  },
  watch: {
    filteredConflicts: function () {
      // Re-calculate all conflicts when the master conflicts dictionary changes
      this.$nextTick(function () {
        // MUST wait for all data to finish resolving when panel info has been
        // updated before recalculating conflicts
        this.deactivatePanelConflicts()
        this.activatePanelConflicts()
      })
    },
  },
  mounted: function () {
    this.$nextTick(function () {
      // MUST to wait for DOM to resolve on initial load before calculating
      // the conflicts
      this.activatePanelConflicts()
    })
  },
  computed: {
    teams: function () {
      return _.map(this.panelTeams, dt => dt.team)
    },
    adjudicators: function () {
      return _.map(this.panelAdjudicators, da => da.adjudicator)
    },
    institutionIDs: function () {
      // Counterpart to adjudicatorIds and teamIds property on DebatePanel; but calculated from
      // institution clashes rather than object IDs. These are not unique.

      let adjInstitutionalClashes = _.map(this.adjudicators, 'conflicts.clashes.institution')
      const adjInstitutionalClashesIDs = _.flatten(adjInstitutionalClashes).map(clash => clash.id)

      let teamInstitutionalClashes = _.map(this.teams, 'conflicts.clashes.institution')
      let teamInstitutionalClashIDs = []
      _.flatten(teamInstitutionalClashes).forEach(clash => {
        if (clash !== undefined) {
          if (clash.id !== undefined) {
            teamInstitutionalClashIDs.push(clash.id)
          }
        }
      })
      // We don't want teams of the same institution clashing each other; so never allow dupe IDs
      teamInstitutionalClashIDs = _.uniq(teamInstitutionalClashIDs)

      return [...adjInstitutionalClashesIDs, ...teamInstitutionalClashes]
    },
    allConflicts: function () {
      // Create an array of conflicts gathered from each team or adjudicator
      const allAdjConflicts = _.map(this.adjudicators, adj => adj.conflicts)
      const allTeamConflicts = _.map(this.teams, team => team.conflicts)
      return [...allAdjConflicts, ...allTeamConflicts]
    },
    filteredConflicts: function () {
      // Traverse the combined conflicts object and delete those not relevant
      // to the panel. This allows us to (later) activate all the leftovers
      const subset = {
        clashes: { adjudicator: [], institution: [], team: [] },
        histories: { adjudicator: [], institution: [], team: [] },
      }
      const self = this
      _.forEach(this.allConflicts, (adjOrTeamsConflicts) => {
        // For all of the panel conflicts
        self.forEachConflict(adjOrTeamsConflicts, (conflict, type, clashOrHistory) => {
          // Drill down into each adj/teams conflicts and filter out those
          // that cannot apply to the panel as-is
          if (self.checkIfInPanel(conflict, type, clashOrHistory)) {
            subset[clashOrHistory][type].push(conflict)
          }
        })
      })
      return subset
    },
  },
  methods: {
    deactivatePanelConflicts: function () {
      // Turn off all conflicts that might remain from previous panellists who
      // have been moved on
      const self = this
      if (this.debugMode) {
        console.log('Deactivate panel conflicts for', this.debateId)
      }
      _.forEach(this.adjudicatorIds, (id) => {
        self.resetConflictsFor('adjudicator', id, 'panel')
      })
      _.forEach(this.teamIds, (id) => {
        self.resetConflictsFor('team', id, 'panel')
      })
    },
    activatePanelConflicts: function () {
      // Turn on all conflicts by activating what has been set by
      // filteredPanelConflicts(). Calls/happens when a panel updates
      const self = this
      if (this.debugMode) {
        console.log('Activate panel conflicts for', this.debateId)
      }
      this.forEachConflict(this.filteredConflicts, (conflict, type, clashOrHistory) => {
        if (type === 'institution') {
          self.activatePanelInstitutionalConflict(conflict)
        } else {
          self.sendConflict(conflict, type, type, 'panel', clashOrHistory)
        }
      })
    },
    activatePanelInstitutionalConflict: function (conflict) {
      // For institutional conflicts within a panel we want to send them
      // out in a targetted fashion (unlike for say hover-overs where we
      // can do a global broadcast by institutional ID); that is to say we
      // need to find and target just the teams/adjs who need them and then
      // target those items specifically
      const self = this

      // Find teams with an institutional conflict that matches
      const teamsMatches = _.filter(this.teams, (team) => {
        const teamInstitutions = team.conflicts.clashes.institution
        const institutionIDs = _.map(teamInstitutions, 'id')
        if (institutionIDs.indexOf(conflict.id) !== -1) {
          return true
        }
        return false
      })

      // Find adjs with an institutional conflict that matcvhes
      const adjsMatches = _.filter(this.adjudicators, (adj) => {
        const adjudicatorsInstitutions = adj.conflicts.clashes.institution
        const institutionIDs = _.map(adjudicatorsInstitutions, 'id')
        if (institutionIDs.indexOf(conflict.id) !== -1) {
          return true
        }
        return false
      })

      // Activate any matches
      if (adjsMatches.length > 0 || teamsMatches.length > 0) {
        _.forEach(adjsMatches, (adj) => {
          self.sendConflict(adj, 'adjudicator', 'institution', 'panel', 'clashes')
        })
        _.forEach(teamsMatches, (team) => {
          self.sendConflict(team, 'team', 'institution', 'panel', 'clashes')
        })
      }
    },
    checkIfInPanel: function (conflict, type) {
      // For a given conflict from a team/adj check if it can actually apply to the panel
      if (type === 'institution') {
        if (this.institutionIDs.filter(id => id === conflict.id).length > 1) {
          // For institutional conflicts there will always be at least one matching ID from the
          // originator; to identify a conflict we need to find if the ID occurs again
          return true
        }
      } else if (type === 'team' && _.includes(this.teamIds, conflict.id)) {
        return true // Conflicted team is present in panel
      } else if (type === 'adjudicator' && _.includes(this.adjudicatorIds, conflict.id)) {
        return true // Conflicted adjudicator is present in panel
      }
      return false
    },
  },
}
</script>
