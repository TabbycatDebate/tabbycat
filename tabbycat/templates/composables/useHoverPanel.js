import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useHoverPanel () {
  const store = useDragAndDropStore()

  const showHoverPanel = (subject, type) => {
    store.setHoverPanel({ subject, type })
  }

  const hideHoverPanel = () => {
    store.unsetHoverPanel()
  }

  return { showHoverPanel, hideHoverPanel }
}
