<script>
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams

  computed: {
    conflictsToSearch: function() {
      var a = _.map(this.panel, function(panellist) {
        return panellist.adjudicator.conflicts
      })
      var b = _.map(this.teams, function(team) {
        return team.conflicts
      })
      return a.concat(b)
    },
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
  },
  created: function () {
    var eventCode = 'check-clashes-for-debate-' + this.debateId
    this.$eventHub.$on(eventCode, this.checkForPanelClashes)
  },
  methods: {
    checkForPanelClashes: function(unset=true) {
      var self = this
      // Turn off all conflicts that might remain from beforehand
      if (unset) {
        _.forEach(this.teams, function(team) {
          self.$eventHub.$emit('unset-conflicts-for-team-' + team.id, 'panel')
        })
        _.forEach(this.panel, function(panellist) {
          self.$eventHub.$emit('unset-conflicts-for-team-' + panellist.adjudicator.id, 'panel')
        })
      }
      // Then search through the list of given conflicts across teams/adjs
      _.forEach(this.conflictsToSearch, function(conflictable) {
        _.forEach(conflictable, function(conflictsCategories, clashOrHistory) {
          _.forEach(conflictsCategories, function(conflictsList, conflictType) {
            if (conflictsList) {
              _.forEach(conflictsList, function(conflict) {
                self.checkIfInPanel(conflict, conflictType, clashOrHistory)
              })
            }
          })
        })
      })
    },
    checkIfInPanel: function(conflict, conflictType, clashOrHistory) {
      if (clashOrHistory === 'clashes') {
        var conflictedId = conflict
      }
      if (clashOrHistory === 'histories') {
        var conflictedId = conflict.id
      }
      if (conflictType === 'institution') {
        return // TODO
      }
      if (conflictType === 'team' && !_.includes(this.teamIds, conflictedId)) {
        return // team not present
      }
      if (conflictType === 'adjudicator' && !_.includes(this.adjudicatorIds, conflictedId)) {
        return // adj not present
      }
      var eventCode = 'set-conflicts-for-' + conflictType + '-' + conflictedId
      if (clashOrHistory === 'clashes') {
        this.$eventHub.$emit(eventCode, 'panel', conflictType, true)
      } else if (clashOrHistory === 'histories') {
        this.$eventHub.$emit(eventCode, 'panel', 'histories', conflict.ago)
      }
    }
  },
  mounted: function () {
    this.checkForPanelClashes(false)
  },
}
</script>
