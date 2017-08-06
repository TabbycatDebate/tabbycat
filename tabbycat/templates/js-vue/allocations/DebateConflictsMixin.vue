<script>
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams

  computed: {
    conflictablesToSearch: function() {
      var a = _.map(this.debateAdjudicators, function(da) {
        return da.adjudicator
      })
      var b = _.map(this.debateTeams, function(dt) {
        return dt.team
      })
      return a.concat(b)
    },
    adjudicatorIds: function() {
      return _.map(this.debateAdjudicators, function(da) {
        return da.adjudicator.id
      })
    },
    teamIds: function() {
      return _.map(this.debateTeams, function(dt) {
        return dt.team.id
      })
    },
  },
  watch: {
    panel: function() {
      this.$nextTick(function () {
        this.checkForPanelClashes() // NEED to wait for DOM updates to trigger
      })
    }
  },
  methods: {
    checkForPanelClashes: function(unset=true) {
      var self = this
      // Turn off all conflicts that might remain from beforehand
      if (unset) {
        _.forEach(this.debateTeams, function(dt) {
          self.$eventHub.$emit('unset-conflicts-for-team-' + dt.team.id, 'panel')
        })
        _.forEach(this.debateAdjudicators, function(da) {
          self.$eventHub.$emit('unset-conflicts-for-adjudicator-' + da.adjudicator.id, 'panel')
        })
      }
      // Then search through the list of given conflicts across teams/adjs
      _.forEach(this.conflictablesToSearch, function(conflictable) {
        _.forEach(conflictable.conflicts, function(conflictsCategories, clashOrHistory) {
          _.forEach(conflictsCategories, function(conflictsList, conflictType) {
            if (conflictsList) {
              _.forEach(conflictsList, function(conflict) {
                if (conflictType === 'institution') {
                  self.checkIfInPanelWithInstitution(conflict, conflictable)
                } else {
                  self.checkIfInPanel(conflict, conflictType, clashOrHistory)
                }
              })
            }
          })
        })
      })
    },
    checkIfInPanel: function(conflict, conflictType, clashOrHistory) {
      if (clashOrHistory === 'clashes') {
        var conflictedId = conflict
      } else if (clashOrHistory === 'histories') {
        var conflictedId = conflict.id
      }
      if ( (conflictType === 'team' && !_.includes(this.teamIds, conflictedId)) ||
           (conflictType === 'adjudicator' && !_.includes(this.adjudicatorIds, conflictedId)) ) {
        return // team or adj not present
      }
      var eventCode = 'set-conflicts-for-' + conflictType + '-' + conflictedId
      if (clashOrHistory === 'clashes') {
        this.$eventHub.$emit(eventCode, 'panel', conflictType, true)
      } else if (clashOrHistory === 'histories') {
        this.$eventHub.$emit(eventCode, 'panel', 'histories', conflict.ago)
      }
    },
    checkIfInPanelWithInstitution: function(conflict, conflictingItem) {
      var self = this
      _.forEach(this.debateTeams, function(dt) {
        var team = dt.team
        if ( (team.institution.id === conflict && team !== conflictingItem) &&
             (_.has(conflictingItem, 'score')) ) {
          // Don't self-conflict and don't allow team-team institution conflicts
          var eventCode = 'set-conflicts-for-team-' + team.id
          self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
          // Reverse the conflict (incase conflicting not own institution)
          var eventCode = 'set-conflicts-for-adjudicator-' + conflictingItem.id
          self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
        }
      })
      _.forEach(this.debateAdjudicators, function(da) {
        var adj = da.adjudicator
        if (adj.institution.id === conflict && adj !== conflictingItem) {
          var eventCode = 'set-conflicts-for-adjudicator-' + adj.id
          self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
          // Reverse the conflict (incase conflicting not own institution)
          var eventCode = 'set-conflicts-for-adjudicator-' + conflictingItem.id
          self.$eventHub.$emit(eventCode, 'panel', 'institution', true)
        }
      })
    }
  },
  mounted: function () {
    this.$nextTick(function () {
      this.checkForPanelClashes(false)  // Need to wait for DOM
    })
  },
}
</script>
