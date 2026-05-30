import { computed } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'
import { useModalError } from './useModalError.js'

export function useEditEitherAdjudicators ({ allDebatesOrPanels }) {
  const store = useDragAndDropStore()
  const { showErrorAlert } = useModalError()

  const getUnallocatedItemFromDebateOrPanel = (debateOrPanel) => {
    const itemIDs = []
    for (const positionAdjudicators of Object.entries(debateOrPanel.adjudicators)) {
      positionAdjudicators[1].forEach((adjudicator) => {
        itemIDs.push(Number(adjudicator))
      })
    }
    return itemIDs
  }

  const getAllocation = (debateID) => {
    if (debateID === null) {
      return null
    }
    if (!Object.prototype.hasOwnProperty.call(allDebatesOrPanels.value, debateID)) {
      const explanation = `A change to the allocation may have been unable to be fulfilled by the
                           server as there was no matching debate on this page. Refresh this page
                           to bring its copy of debates back in-sync with the server.`
      showErrorAlert(explanation, null, 'Unrecognised Debate', 'text-danger', true, true)
      return null
    }
    let newAllocation = allDebatesOrPanels.value[debateID].adjudicators
    newAllocation = JSON.parse(JSON.stringify(newAllocation))
    return newAllocation
  }

  const addToAllocation = (allocation, adjudicatorID, position) => {
    allocation[position].push(adjudicatorID)
    return allocation
  }

  const removeFromAllocation = (allocation, adjudicatorID, position) => {
    allocation[position] = allocation[position].filter(id => id !== adjudicatorID)
    return allocation
  }

  const swapPanels = (draggedPanelID, droppedPanelID) => {
    const fromPanellists = getAllocation(draggedPanelID.panel)
    const toPanellists = getAllocation(droppedPanelID.assignment)

    const allocationChanges = []
    allocationChanges.push({ id: draggedPanelID.panel, adjudicators: toPanellists })
    allocationChanges.push({ id: droppedPanelID.assignment, adjudicators: fromPanellists })

    store.updateDebatesOrPanelsAttribute({ adjudicators: allocationChanges })
  }

  const moveAdjudicator = (dragData, dropData) => {
    if ((dragData.assignment === dropData.assignment && dragData.position === dropData.position) ||
        (dragData.assignment === null && dropData.assignment === null)) {
      return
    }

    const allocationChanges = []
    const adjudicatorsSetModified = [dragData.item]
    let fromAllocation = dragData.assignment === undefined
      ? getAllocation(dragData.panel)
      : getAllocation(dragData.assignment)
    let toAllocation = getAllocation(dropData.assignment)

    if (dragData.assignment === dropData.assignment) {
      toAllocation = fromAllocation
    }

    if (dragData.panel) {
      allocationChanges.push({ id: dragData.panel, adjudicators: { C: [], P: [], T: [] } })
    } else {
      if (fromAllocation !== null) {
        fromAllocation = removeFromAllocation(fromAllocation, dragData.item, dragData.position)
      }
      if (toAllocation !== null) {
        toAllocation = addToAllocation(toAllocation, dragData.item, dropData.position)
        if (toAllocation.C.length > 1) {
          const existingChair = toAllocation.C[0]
          adjudicatorsSetModified.push(existingChair)
          toAllocation = removeFromAllocation(toAllocation, existingChair, 'C')
          if (dragData.assignment !== null) {
            fromAllocation = addToAllocation(fromAllocation, existingChair, dragData.position)
          }
        }
      }

      if (fromAllocation !== null) {
        allocationChanges.push({ id: dragData.assignment ?? dragData.panel, adjudicators: fromAllocation })
      }
      if (toAllocation !== null && dragData.assignment !== dropData.assignment) {
        allocationChanges.push({ id: dropData.assignment, adjudicators: toAllocation })
      }
    }

    store.updateDebatesOrPanelsAttribute({ adjudicators: allocationChanges })
    store.updateAllocatableItemModified(adjudicatorsSetModified)
  }

  const showShard = () => {
    window.$?.('#confirmShardModal').modal('show')
  }

  const showAllocate = () => {
    window.$?.('#confirmAllocateModal').modal('show')
  }

  const showPrioritise = () => {
    window.$?.('#confirmPrioritiseModal').modal('show')
  }

  return {
    getUnallocatedItemFromDebateOrPanel,
    swapPanels,
    moveAdjudicator,
    showShard,
    showAllocate,
    showPrioritise,
  }
}
