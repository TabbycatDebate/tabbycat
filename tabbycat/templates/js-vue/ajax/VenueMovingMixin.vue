<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  methods: {
    saveMove(venueId, fromDebateId, toDebateId, dontPushToUnused=false, isSwap=false) {
      var venue = this.allVenuesById[venueId]
      var toDebate = this.debatesById[toDebateId]
      var fromDebate = this.debatesById[fromDebateId]

      if (_.isUndefined(fromDebate)) { // Undefined if coming from unused
        var from = 'unused'
      } else {
        var from = fromDebate.id
      }
      if (_.isUndefined(toDebate)) { // Undefined if going to unused
        var to = 'unused'
      } else {
        var to = toDebate.id
      }

      if (to === 'unused') {
        fromDebate.venue = null
        this.unallocatedItems.push(venue)
      }
      if (from === 'unused') {
        if (toDebate.venue !== null) { // If replacing a venue
          this.unallocatedItems.push(toDebate.venue)
        }
        toDebate.venue = venue
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(venue), 1)
      }
      if (to !== 'unused' && from !== 'unused') {
        if (toDebate.venue !== null) { // If replacing a venue
          fromDebate.venue = toDebate.venue
        } else {
          fromDebate.venue = null
        }
        toDebate.venue = venue
      }
      var debatesToSave = []
      if (to !== 'unused') {
        debatesToSave.push(toDebate)
      }
      if (from !== 'unused') {
        debatesToSave.push(fromDebate)
      }
      var self = this
      _.forEach(debatesToSave, function(debateToSave) {
        var message = 'debate venues of ' + self.niceNameForDebate(debateToSave.id)
        debateToSave.locked = true
        self.ajaxSave(self.roundInfo.saveUrl, debateToSave, message, function(dataResponse) {
          // Replace old debate object with new one
          var oldDebateIndex = self.debates.indexOf(debateToSave)
          self.debates.splice(oldDebateIndex, 1, dataResponse)
          console.log("    VUE: Loaded new debate for " + self.niceNameForDebate(dataResponse.id))
        })
      })
    },
  }
}
</script>