<script>
// This transmits an items conflicts to the VueX store; other items then need to respond to it
// Must set action of @mouseenter="showHoverConflicts( SUBJECT_ID, SUBJECT_TYPE )
// Must set action of @mouseleave="hideHoverConflicts( SUBJECT_ID, SUBJECT_TYPE )
import { mapGetters, mapMutations } from 'vuex'

export default {
  methods: {
    showHoverConflicts: function (itemId, itemType) {
      // TODO get clashes and conflicts by type
      let clashes = null
      let histories = null
      if (itemType === 'team') {
        clashes = this.teamClashesForItem(itemId)
        histories = this.teamHistoriesForItem(itemId)
      } else if (itemType === 'adjudicator') {
        clashes = this.adjudicatorClashesForItem(itemId)
        histories = this.adjudicatorHistoriesForItem(itemId)
      }
      this.setHoverConflicts({ clashes: clashes, histories: histories })
    },
    hideHoverConflicts: function () {
      this.unsetHoverConflicts()
    },
    ...mapMutations(['setHoverConflicts', 'unsetHoverConflicts']),
  },
  computed: {
    ...mapGetters(['adjudicatorClashesForItem', 'teamClashesForItem',
      'adjudicatorHistoriesForItem', 'teamHistoriesForItem']),
  },
}
</script>
