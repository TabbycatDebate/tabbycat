<script>
import _ from 'lodash'

export default {

  methods: {
    sendConflict: function(conflict, type, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to activate a given conflict type
      var eventCode = 'set-conflicts-for-' + type

      var state = true
      if (clashOrHistory === 'histories') {
        var state = conflict.ago // Override; histories use int values
      }

      this.debugLog("_ " + eventCode, 1, conflict.id,
                           hoverOrPanel, clashOrHistory, type, state)
      this.$eventHub.$emit(eventCode, conflict.id,
                           hoverOrPanel, clashOrHistory, type, state)
    },
    unsendConflict: function(id, type, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to deactivate a given conflict type
      var eventCode = 'unset-conflicts-for-' + type

      this.debugLog(eventCode, 1, id,
                    hoverOrPanel, clashOrHistory, type, false)
      this.$eventHub.$emit(eventCode, id, hoverOrPanel, clashOrHistory,
                                      type, false)
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
                       hoverOrPanel, clashOrHistory, type, state) {
      if (_.isUndefined(this.conflictable)) {
        var source = "panel"
      } else {
        var source = this.conflictable.id + " " + this.conflictableType
      }
      console.debug("\t".repeat(tabLevel) + title,
                    '\t for', source,
                    '\t as active vs', type, ' #', id,
                    '\t', hoverOrPanel, '\t', clashOrHistory)
    },
  }

}
</script>