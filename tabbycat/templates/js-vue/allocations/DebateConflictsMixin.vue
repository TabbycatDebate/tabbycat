<script>
import ConflictsCoordinatorMixin from '../allocations/ConflictsCoordinatorMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between ConflictsCoordinatorMixin
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  // It relies on both components having a conflicts/histories dictionary;
  // which in the case of a Debate only lists the adjudicators present
  // This the same logic can be used to check for conflicts/histories

  mixins: [ConflictsCoordinatorMixin],
  computed: {
    adjudicatorIds: function() {
      return _.map(this.panel, function(panellist) {
        return panellist.adjudicator.id
      })
    },
    teamIds: function() {
      return _.map(this.teams, function(team) {
        return team.id
      })
    },
    filteredClashes: function() {
      // For the received conflicts (which are given per-adjudicator and contain
      // all of their possible histories/conflicts we need to go through and
      // delete the ones do not match to teams/adjs present in the debate
      var self = this
      var filteredConflicts = _.forEach(this.conflicts, function(conflictsByAdj) {
        conflictsByAdj.team = _.filter(conflictsByAdj.team, function(conflict) {
          return _.includes(self.teamIds, conflict)
        })
        conflictsByAdj.institution = null // TODO: figure out to do in panels
        conflictsByAdj.adjudicator = _.filter(conflictsByAdj.adjudicator, function(conflict) {
          return _.includes(self.adjudicatorIds, conflict)
        })
      })
      return filteredConflicts
    },
    filteredHistories: function() {
      // TODO: for these conflicts need to go through and delete the ones that
      // don't have teams/adjudicators who are also present in the debate
      var self = this
      var filteredConflicts = _.forEach(this.seens, function(seensByAdj) {
        seensByAdj.team = _.filter(seensByAdj.team, function(seen) {
          return _.includes(self.teamIds, seen)
        })
        seensByAdj.adjudicator = _.filter(seensByAdj.adjudicator, function(seen) {
          return _.includes(self.adjudicatorIds, seen)
        })
      })
      return this.conflicts
    }
  },
  mounted: function () {
    this.checkForPanelClashes()
  },
  methods: {
    checkForPanelClashes() {
      var self = this
      _.forEach(this.panel, function(panellist) {
        // Get all the conflicts for a given pannellist from the inherited debate-relevant list
        self.setOrUnsetConflicts(panellist.adjudicator, 'adjudicator', 'panel', false) // First unset to clear
        self.setOrUnsetConflicts(panellist.adjudicator, 'adjudicator', 'panel', true) // Then reset
      })
    }
  },
  watch: {
    panel: function() {
      this.checkForPanelClashes()
    },
  }
}
</script>
