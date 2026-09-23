import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useHoverConflicts () {
  const store = useDragAndDropStore()

  const showHoverConflicts = (itemId, itemType) => {
    let clashes = null
    let histories = null

    if (itemType === 'team') {
      clashes = store.teamClashesForItem(itemId)
      histories = store.teamHistoriesForItem(itemId)
    } else if (itemType === 'adjudicator') {
      clashes = store.adjudicatorClashesForItem(itemId)
      histories = store.adjudicatorHistoriesForItem(itemId)
    } else if (itemType === 'panel') {
      clashes = store.panelClashesOrHistoriesForItem(itemId, 'clashes')
      histories = store.panelClashesOrHistoriesForItem(itemId, 'histories')
    } else {
      console.error('Unrecognised conflict type provided to showHoverConflicts()')
    }

    store.setHoverConflicts({ clashes, histories })
  }

  const hideHoverConflicts = () => {
    store.unsetHoverConflicts()
  }

  return { showHoverConflicts, hideHoverConflicts }
}
