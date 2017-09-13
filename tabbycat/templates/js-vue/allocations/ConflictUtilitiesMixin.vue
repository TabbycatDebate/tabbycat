<script>
import _ from 'lodash'

export default {

  methods: {
    unsendConflict: function(id, type, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to deactivate a given conflict (passes to the Conflictable)
      var eventCode = 'unset-conflicts-for-' + type
      console.debug('\t', eventCode, id, hoverOrPanel, clashOrHistory, type)
      this.$eventHub.$emit(eventCode, id, hoverOrPanel, clashOrHistory, type, false)
    },
    sendConflict: function(conflict, type, hoverOrPanel, clashOrHistory) {
      // Issue a Vue message to activate a given conflict (passes to the Conflictable)
      var eventCode = 'set-conflicts-for-' + type

      if (clashOrHistory === 'clashes') {
        var state = true
      } else if (clashOrHistory === 'histories') {
        var state = conflict.ago
      }
      console.debug('\t', eventCode, conflict.id, hoverOrPanel, clashOrHistory, type)
      this.$eventHub.$emit(eventCode, conflict.id, hoverOrPanel, clashOrHistory, type, state)
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
    }
  }

}
</script>