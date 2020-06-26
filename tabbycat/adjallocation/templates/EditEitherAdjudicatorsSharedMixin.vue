<script>
// Mixin for shared logic between editing debate adjudicators and editing panel adjudicators
import DragAndDropContainerMixin from '../../templates/allocations/DragAndDropContainerMixin.vue'
import ModalForSharding from '../../templates/modals/ModalForSharding.vue'
import ModalForPrioritising from '../../templates/modals/ModalForPrioritising.vue'
import ModalForAllocating from '../../templates/modals/ModalForAllocating.vue'

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
      const itemIDs = []
      for (const positionAdjudicators of Object.entries(debateOrPanel.adjudicators)) {
        positionAdjudicators[1].forEach((adjudicator) => {
          itemIDs.push(Number(adjudicator))
        })
      }
      return itemIDs
    },
    getAllocation: function (debateID) {
      if (debateID === null) {
        return null // Moving to or from Unused
      }
      if (!Object.prototype.hasOwnProperty.call(this.allDebatesOrPanels, debateID)) {
        const explanation = `A change to the allocation may have been unable to be fulfilled by the
                           server as there was no matching debate on this page. Refresh this page
                           to bring its copy of debates back in-sync with the server.`
        this.showErrorAlert(explanation, null, 'Unrecognised Debate', 'text-danger', true, true)
        return null // Socket returned a debateID that doesn't exist locally
      }
      let newAllocation = this.allDebatesOrPanels[debateID].adjudicators
      newAllocation = JSON.parse(JSON.stringify(newAllocation)) // Clone so non-reactive
      return newAllocation
    },
    addToAllocation: function (allocation, adjudicatorID, position) {
      allocation[position].push(adjudicatorID)
      return allocation
    },
    removeFromAllocation: function (allocation, adjudicatorID, position) {
      // Copy existing allocation from VueX state
      // Loop over all adjudicator positions and remove matching adjudicators
      allocation[position] = allocation[position].filter(id => id !== adjudicatorID)
      return allocation
    },
    moveAdjudicator: function (dragData, dropData) {
      if ((dragData.assignment === dropData.assignment && dragData.position === dropData.position) ||
          (dragData.assignment === null && dropData.assignment === null)) {
        return // Moving from Unused to Unused; or from the same position/debate and back again
      }
      const allocationChanges = []
      const adjudicatorsSetModified = [dragData.item]
      let fromAllocation = this.getAllocation(dragData.assignment)
      let toAllocation = this.getAllocation(dropData.assignment)
      if (dragData.assignment === dropData.assignment) {
        toAllocation = fromAllocation // If repositioning we don't want two distinct allocations
      }

      // Re-form the assignments
      if (fromAllocation !== null) { // Not moving FROM Unused
        fromAllocation = this.removeFromAllocation(fromAllocation, dragData.item, dragData.position)
      }
      if (toAllocation !== null) { // Not moving TO Unused
        toAllocation = this.addToAllocation(toAllocation, dragData.item, dropData.position)
        // If the adj was moved to a chair position there are now two; need to move or swap
        if (toAllocation.C.length > 1) {
          const existingChair = toAllocation.C[0]
          adjudicatorsSetModified.push(existingChair)
          toAllocation = this.removeFromAllocation(toAllocation, existingChair, 'C')
          if (dragData.assignment !== null) {
            // Dragging from a chair to chair; thus move existing chair to chair in original debate
            fromAllocation = this.addToAllocation(fromAllocation, existingChair, dragData.position)
          }
        }
      }

      // Send results
      if (fromAllocation !== null) {
        allocationChanges.push({ id: dragData.assignment, adjudicators: fromAllocation })
      }
      if (toAllocation !== null && dragData.assignment !== dropData.assignment) {
        allocationChanges.push({ id: dropData.assignment, adjudicators: toAllocation })
      }
      this.$store.dispatch('updateDebatesOrPanelsAttribute', { adjudicators: allocationChanges })
      this.$store.dispatch('updateAllocableItemModified', adjudicatorsSetModified)
    },
    showShard: function () {
      $('#confirmShardModal').modal('show')
    },
  },
}
</script>
