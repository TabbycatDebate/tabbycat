<script>
import _ from 'lodash'

export default {

  methods: {
    sendConflict: function(conflict, eventType, conflictType, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to activate a given conflict type
      var eventCode = 'set-conflicts-for-' + eventType

      var state = true
      if (clashOrHistory === 'histories') {
        var state = conflict.ago // Override; histories use int values
      }

      this.debugLog(       eventCode, 1, conflict.id, hoverOrPanel, clashOrHistory, eventType, conflictType, state)
      this.$eventHub.$emit(eventCode, conflict.id, hoverOrPanel, clashOrHistory, eventType, conflictType, state)
    },
    unsendConflict: function(id, eventType, conflictType, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to deactivate a given conflict type
      var eventCode = 'unset-conflicts-for-' + eventType

      this.debugLog(       eventCode, 1, id, hoverOrPanel, clashOrHistory, eventType, conflictType, false)
      this.$eventHub.$emit(eventCode, id, hoverOrPanel, clashOrHistory, eventType, conflictType, false)
    },
    forEachConflict: function(conflictsList, callBack) {
      // Traverses a list of conflicts and calls the provided function on each
      // individual conflict object
      var self = this
      _.forEach(conflictsList, function(types, clashOrHistory) {
        // Descending into clash or history
        _.forEach(types, function(conflicts, type) {
          // Descending into adjudicator or institution or team
          _.forEach(conflicts, function(conflict) {
            // Descending into each inidividual conflict and returning its
            // attributes to the call back function
            callBack(conflict, type, clashOrHistory)
          })
        })
      })
    },
    debugLog: function(title, tabLevel, id,
                       hoverOrPanel, clashOrHistory, eventType, conflictType, state) {
      if (_.isUndefined(this.conflictable)) {
        var source = "panel"
      } else {
        var source = this.conflictable.id + " " + this.conflictableType
      }
      var spacer = "                      "
      console.debug(("\t".repeat(tabLevel) + title + spacer).substring(0, 35),
        ('to ' + conflictType + ' #' + id + spacer).substring(0, 25),
        ('via ' + hoverOrPanel + '' + spacer).substring(0, 40),
        (' as ' + state + ' for ' + clashOrHistory + spacer).substring(0, 35)
      )
    },
  }

}
</script>