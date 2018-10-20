<script>
// Mixin for shared logic between editing debate adjudicators and editing panel adjudicators
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import ModalForSharding from '../../utils/templates/modals/ModalForSharding.vue'
import ModalForPrioritising from '../../utils/templates/modals/ModalForPrioritising.vue'
import ModalForAllocating from '../../utils/templates/modals/ModalForAllocating.vue'

import DebateOrPanelImportance from './DebateOrPanelImportance.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'
import DebateOrPanelAdjudicators from './DebateOrPanelAdjudicators.vue'

export default {
  mixins: [DragAndDropContainerMixin],
  components: {
    ModalForSharding,
    ModalForPrioritising,
    ModalForAllocating,
    DebateOrPanelImportance,
    DraggableAdjudicator,
    DebateOrPanelAdjudicators,
  },
  data: () => ({
    unallocatedComponent: DraggableAdjudicator,
  }),
  methods: {
    getUnallocatedItemFromDebateOrPanel (debateOrPanel) {
      // Return the IDs of the adjudicators allocated to this debate
      let itemIDs = []
      for (const positionAdjudicators of Object.entries(debateOrPanel.adjudicators)) {
        positionAdjudicators[1].forEach((adjudicator) => {
          itemIDs.push(Number(adjudicator))
        })
      }
      return itemIDs
    },
  },
}
</script>
