<script>
import _ from 'lodash'

export default {

  methods: {
    sendConflict: function (conflict, eventType, conflictType, hoverOrPanel,
                           clashOrHistory, issuerType) {
      // Issue a Vue message to activate a given conflict type
      var eventCode = 'set-conflicts-for-' + eventType
      var state = true
      if (clashOrHistory === 'histories') {
        var state = conflict.ago // Override; histories use int values
      }
      if (this.debugMode) {
        this.debugLog(eventCode, 1, conflict.id, hoverOrPanel, clashOrHistory,
                      eventType, conflictType, state, issuerType)
      }

      this.$eventHub.$emit(eventCode, conflict.id, hoverOrPanel, clashOrHistory,
                           eventType, conflictType, state, issuerType)
    },
    unsendConflict: function (conflict, eventType, conflictType, hoverOrPanel,
                             clashOrHistory, issuerType) {
      // Issue a Vue message to deactivate a given conflict type
      var eventCode = 'unset-conflicts-for-' + eventType
      if (this.debugMode) {
        this.debugLog(eventCode, 1, conflict.id, hoverOrPanel, clashOrHistory,
                      eventType, conflictType, false, issuerType)
      }
      this.$eventHub.$emit(eventCode, conflict.id, hoverOrPanel, clashOrHistory,
                           eventType, conflictType, false, issuerType)
    },
    resetConflictsFor: function (entityType, entityID, hoverOrPanel) {
      // Deactivate all conflicts; such as when a panel changes composition
      var eventCode = 'reset-conflicts-for-' + entityType + '-' + entityID
      if (this.debugMode) {
        this.debugLog(eventCode, 1, entityID, hoverOrPanel, 'both',
                      entityType, 'all', false, 'panel change')
      }
      this.$eventHub.$emit(eventCode, hoverOrPanel)
    },
    forEachConflict: function (conflictsList, callBack) {
      // Utility function that traverses/loops over a list of conflicts and
      // calls the provided function on each individual conflict object
      // Prevents a whole bunch of nested forEaches popping up elsewhere
      var self = this
      _.forEach(conflictsList, function (types, clashOrHistory) {
        // Descending into clash or history
        _.forEach(types, function (conflicts, type) {
          // Descending into adjudicator or institution or team
          _.forEach(conflicts, function (conflict) {
            // Descending into each inidividual conflict and returning its
            // attributes to the call back function
            callBack(conflict, type, clashOrHistory)
          })
        })
      })
    },
    debugLog: function (title, tabLevel, id, hoverOrPanel, clashOrHistory,
                       eventType, conflictType, state, issuerType) {
      // Crappy utility for trying to trace when/why conflicts dont show up
      // the spacer business is so it will print nice to console
      if (_.isUndefined(this.conflictable)) {
        var source = "panel"
      } else {
        var source = this.conflictable.id + " " + this.conflictableType
      }
      var spacer = "                                                        "
      console.info(
        ("\t".repeat(tabLevel) + title + spacer).substring(0, 45 - (tabLevel * 4)),
        ('to ' + eventType + ' #' + id + spacer).substring(0, 25),
        ('of type ' + conflictType + spacer).substring(0, 25),
        (' as ' + state + ' for ' + clashOrHistory + ' / ' + hoverOrPanel + spacer).substring(0, 35),
        (' from a ' + issuerType).substring(0, 15)
      )
    },
  }

}
</script>