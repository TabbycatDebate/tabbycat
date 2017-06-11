<script>
import MovingMixin from '../ajax/MovingMixin.vue'
import _ from 'lodash'

export default {
  mixins: [MovingMixin],
  methods: {
    saveMoveForType(venueId, fromDebate, toDebate) {
      var venue = this.allVenuesById[venueId]
      // Data Logic
      if (toDebate === 'unused') {
        fromDebate.venue = null
        this.unallocatedItems.push(venue)
      }
      if (fromDebate === 'unused') {
        if (toDebate.venue !== null) {
          // If replacing an in-place venue
          this.unallocatedItems.push(toDebate.venue)
        }
        toDebate.venue = venue
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(venue), 1)
      }
      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        if (toDebate.venue !== null) {
          // If replacing an in-place venue
          fromDebate.venue = toDebate.venue
        } else {
          fromDebate.venue = null
        }
        toDebate.venue = venue
      }
      // Saving
      var debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      this.postModifiedDebates(debatesToSave, 'debate venues of ')
    },
  }
}
</script>