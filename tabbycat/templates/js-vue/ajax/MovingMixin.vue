<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  methods: {
    niceNameForDebate: function(debateId) {
      if (debateId === 'unused') {
        return 'unused'
      }
      var debate = this.debatesById[debateId]
      // Used for debugging
      var niceName = "debate " + debate.id + " ("
      _.forEach(debate.teams, function(team) {
        niceName += team.short_name + ", "
      })
      niceName = niceName.substring(0, niceName.length - 2)
      niceName += ")"
      return niceName
    },
    saveMove(movedItemId, fromDebateId, toDebateId, toPosition=null) {
      var toDebate = this.debatesById[toDebateId]
      var fromDebate = this.debatesById[fromDebateId]
      if (_.isUndefined(fromDebate)) { // Undefined if coming from unused
        fromDebate = 'unused'
      }
      if (_.isUndefined(toDebate)) { // Undefined if going to unused
        toDebate = 'unused'
      }
      this.saveMoveForType(movedItemId, fromDebate, toDebate, toPosition)
    },
    debateCheckIfShouldSave(debate) {
      return true
    },
    determineDebatesToSave(fromDebate, toDebate) {
      if (fromDebate === toDebate) {
        return [toDebate]
      }
      var debatesToSave = []
      if (toDebate !== 'unused' && this.debateCheckIfShouldSave(toDebate)) {
        debatesToSave.push(toDebate)
      }
      if (fromDebate !== 'unused' && this.debateCheckIfShouldSave(fromDebate)) {
        debatesToSave.push(fromDebate)
      }
      return debatesToSave
    },
    postModifiedDebates(debatesToSave, messageStart) {
      var self = this
      _.forEach(debatesToSave, function(debateToSave) {
        var message = messageStart + self.niceNameForDebate(debateToSave.id)
        debateToSave.locked = true
        self.ajaxSave(self.roundInfo.saveUrl, debateToSave, message, function(dataResponse) {
          // Replace old debate object with new one
          var oldDebateIndex = self.debates.indexOf(debateToSave)
          if (oldDebateIndex !== -1) {
            self.debates.splice(oldDebateIndex, 1, dataResponse)
            console.log("    VUE: Loaded new debate for " + self.niceNameForDebate(dataResponse.id))
          } else {
            console.log("Shouldn't happen; couldnt find old debates position")
          }
        })
      })
    }
  }
}
</script>