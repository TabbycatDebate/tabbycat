<script>
import MovingMixin from '../ajax/MovingMixin.vue'
import _ from 'lodash'

export default {
  mixins: [MovingMixin],
  methods: {
    saveMoveForType(venueId, fromDebate, toDebate) {
      var venue = this.allVenuesById[venueId]
      var addToUnused = []
      var removeFromUnused = []
      // Data Logic
      if (toDebate === 'unused') {
        fromDebate.venue = null
        addToUnused.push(venue)
      }
      if (fromDebate === 'unused') {
        if (toDebate.venue !== null) {
          // If replacing an in-place venue
          addToUnused.push(toDebate.venue)
        }
        toDebate.venue = venue
        removeFromUnused.push(venue)
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
      this.postModifiedDebates(debatesToSave, addToUnused, removeFromUnused,
                               'debate venues of ')
    },
  }
}
</script>