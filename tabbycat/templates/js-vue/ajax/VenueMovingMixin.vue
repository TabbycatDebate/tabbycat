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

      var message = 'moved venue ' + venue.name + ' from ' + from + ' to ' + to
      var payload = { moved_item: venue.id, moved_from: from, moved_to: to }
      var self = this
      this.ajaxSave(this.roundInfo.saveUrl, payload, message, function() {
        if (to === 'unused') {
          self.processMoveToUnusedFromDebate(venue, fromDebate, dontPushToUnused)
        } else {
          if (from === 'unused') {
            self.processMoveToDebateFromUnused(venue, toDebate)
          } else {
            if (toDebate.venue === null) {
              self.processMoveToDebateWithoutVenueFromDebate(venue, fromDebate, toDebate)
            } else {
              self.processMoveToDebateWithVenueFromDebate(venue, fromDebate, toDebate, isSwap)
            }
          }
        }
      })
    },
    processMoveToUnusedFromDebate(venue, fromDebate, dontPushToUnused) {
      // Moving to Unused from a debate
      if (!dontPushToUnused) {
        // We don't push to unused when this venue is being removed from an
        // existing debate; ie via processMoveToDebateWithoutVenueFromDebate()
        this.unallocatedItems.push(venue) // Need to push; not append
      }
      fromDebate.venue = null
    },
    processMoveToDebateFromUnused(venue, toDebate) {
      // If moving from unused needed to remove the venue from unallcoated items
      this.unallocatedItems.splice(this.unallocatedItems.indexOf(venue), 1)
      toDebate.venue = venue
    },
    processMoveToDebateWithoutVenueFromDebate(venue, fromDebate, toDebate) {
      // If moving from an existing debate without a venue then retrigger a save
      // as if we were moving to unused but override adding it back to the js data
      toDebate.venue = venue
      this.saveMove(venue.id, fromDebate.id, 'unused', true)
    },
    processMoveToDebateWithVenueFromDebate(venue, fromDebate, toDebate, isSwap) {
      // If moving from one debate to another where both have venues
      // The isSwap override is here to prevent never ending recursive recalls
      // If moving from an existing debate into a debate with a venue; do a swap
      if (!isSwap) {
        this.saveMove(toDebate.venue.id, toDebate.id, fromDebate.id, false, true)
      }
      toDebate.venue = venue
    },
  }
}
</script>