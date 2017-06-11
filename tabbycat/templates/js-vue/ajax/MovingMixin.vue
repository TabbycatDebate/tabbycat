<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  methods: {
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
    determinedDebatesToSave(fromDebate, toDebate) {
      var debatesToSave = []
      if (toDebate !== 'unused' && this.debateCheckIfShouldSave(toDebate) {
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
          self.debates.splice(oldDebateIndex, 1, dataResponse)
          console.log("    VUE: Loaded new debate for " + self.niceNameForDebate(dataResponse.id))
        })
      })
    }
  }
}
</script>