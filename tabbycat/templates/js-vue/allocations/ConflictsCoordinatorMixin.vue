<script>
import _ from 'lodash'

export default {
  props: ['conflicts', 'initialUnallocatedItems', 'roundInfo'],
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('show-conflicts-for', this.setConflicts)
    this.$eventHub.$on('hide-conflicts-for', this.unsetConflicts)
  },
  computed: {

  },
  methods: {
    setConflicts: function(conflictingItem, conflictingItemType) {
      if (conflictingItemType === 'adjudicator') {
        var conflicts = this.conflicts[conflictingItem.id]
        this.$eventHub.$emit('set-conflicts-for', conflictingItem, conflicts, true)
      }
    },
    unsetConflicts: function(conflictingItem, conflictingItemType) {
      if (conflictingItemType === 'adjudicator') {
        var conflicts = this.conflicts[conflictingItem.id]
        this.$eventHub.$emit('set-conflicts-for', conflictingItem, conflicts, false)
      }
    }
  }
}
</script>