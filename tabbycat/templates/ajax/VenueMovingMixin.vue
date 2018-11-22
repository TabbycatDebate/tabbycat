<script>
import MovingMixin from '../ajax/MovingMixin.vue'

export default {
  mixins: [MovingMixin],
  methods: {
    debateCheckIfShouldSave () {
      return true
    },
    saveMoveForType (venueId, fromDebate, toDebate) {
      const venue = this.allVenuesById[venueId]
      const addToUnused = []
      const removeFromUnused = []
      const newFromDebate = fromDebate
      const newToDebate = toDebate
      // Data Logic
      if (newToDebate === 'unused') {
        newFromDebate.venue = null
        addToUnused.push(venue)
      }
      if (newFromDebate === 'unused') {
        if (newToDebate.venue !== null) {
          // If replacing an in-place venue
          addToUnused.push(newToDebate.venue)
        }
        newToDebate.venue = venue
        removeFromUnused.push(venue)
      }
      if (newToDebate !== 'unused' && newFromDebate !== 'unused') {
        if (newToDebate.venue !== null) {
          // If replacing an in-place venue
          newFromDebate.venue = newToDebate.venue
        } else {
          newFromDebate.venue = null
        }
        newToDebate.venue = venue
      }
      // Saving
      const debatesToSave = this.determineDebatesToSave(fromDebate, newToDebate)
      this.postModifiedDebates(
        debatesToSave, addToUnused, removeFromUnused,
        null, 'debate venues of '
      )
    },
  },
}
</script>
