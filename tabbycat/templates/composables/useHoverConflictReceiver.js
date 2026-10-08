import { computed } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useHoverConflictReceiver ({ clashableType, clashableID }) {
  const store = useDragAndDropStore()

  const getConflictsForType = (conflictType) => {
    if (clashableType.value === 'team' && conflictType === 'clash') {
      return store.teamClashesForItem(clashableID.value)
    } else if (clashableType.value === 'team' && conflictType === 'history') {
      return store.teamHistoriesForItem(clashableID.value)
    } else if (clashableType.value === 'adjudicator' && conflictType === 'clash') {
      return store.adjudicatorClashesForItem(clashableID.value)
    } else if (clashableType.value === 'adjudicator' && conflictType === 'history') {
      return store.adjudicatorHistoriesForItem(clashableID.value)
    }
  }

  const hasHoverClashConflict = computed(() => {
    const sourceClashes = store.currentHoverClashes
    if (!sourceClashes) { return false }

    if ('team' in sourceClashes && clashableType.value === 'team') {
      for (const sourceClash of sourceClashes.team) {
        if (sourceClash.id === clashableID.value) {
          return true
        }
      }
    }

    if ('adjudicator' in sourceClashes && clashableType.value === 'adjudicator') {
      for (const sourceClash of sourceClashes.adjudicator) {
        if (sourceClash.id === clashableID.value) {
          return true
        }
      }
    }

    return false
  })

  const hasHoverInstitutionalConflict = computed(() => {
    const sourceClashes = store.currentHoverClashes
    if (!sourceClashes) { return false }

    const itemClashes = getConflictsForType('clash')
    if (!itemClashes) { return false }

    if ('institution' in sourceClashes && 'institution' in itemClashes) {
      for (const sourceClash of sourceClashes.institution) {
        for (const itemClash of itemClashes.institution) {
          if (sourceClash.id === itemClash.id) {
            return true
          }
        }
      }
    }

    return false
  })

  const hasHoverHistoryConflict = computed(() => {
    if (!store.currentHoverHistories) {
      return false
    }

    const sourceHistories = store.currentHoverHistories
    let smallestAgo = 99

    if ('team' in sourceHistories && clashableType.value === 'team') {
      for (const sourceHistory of sourceHistories.team) {
        if (sourceHistory.id === clashableID.value) {
          if (sourceHistory.ago < smallestAgo) {
            smallestAgo = sourceHistory.ago
          }
        }
      }
    }

    if ('adjudicator' in sourceHistories && clashableType.value === 'adjudicator') {
      for (const sourceHistory of sourceHistories.adjudicator) {
        if (sourceHistory.id === clashableID.value) {
          if (sourceHistory.ago < smallestAgo) {
            smallestAgo = sourceHistory.ago
          }
        }
      }
    }

    if (smallestAgo === 99) {
      return false
    }

    return smallestAgo
  })

  const hoverConflictsCSS = computed(() => {
    if (store.currentHoverClashes === null && store.currentHoverHistories === null) {
      return ''
    } else if (hasHoverClashConflict.value) {
      return 'conflictable hover-adjudicator'
    } else if (hasHoverInstitutionalConflict.value) {
      return 'conflictable hover-institution'
    } else if (hasHoverHistoryConflict.value) {
      return `conflictable hover-histories-${hasHoverHistoryConflict.value}-ago`
    }
    return ''
  })

  return {
    hasHoverClashConflict,
    hasHoverInstitutionalConflict,
    hasHoverHistoryConflict,
    hoverConflictsCSS,
  }
}
