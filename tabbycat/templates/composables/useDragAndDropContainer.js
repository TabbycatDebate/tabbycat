import { computed, watchEffect } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'
import { useWebSocket } from './useWebSocket.js'

export function useDragAndDropContainer ({
  initialData,
  getUnallocatedItemFromDebateOrPanel,
  socketBaseLabel = 'debates',
  socketsOverride = null,
}) {
  const store = useDragAndDropStore()

  store.setupInitialData(initialData)

  const sockets = socketsOverride ?? (() => {
    try {
      const currentSeq = (initialData && initialData.round) ? initialData.round.seq : null
      const seqs = new Set()
      if (initialData && Array.isArray(initialData.debatesOrPanels)) {
        initialData.debatesOrPanels.forEach(d => {
          if (d && d.round_seq !== undefined && d.round_seq !== null) {
            seqs.add(String(d.round_seq))
          }
        })
      }
      const ordered = []
      if (currentSeq !== null) {
        ordered.push(`${socketBaseLabel}:${currentSeq}`)
      }
      for (const s of Array.from(seqs).sort((a, b) => Number(a) - Number(b))) {
        const label = `${socketBaseLabel}:${s}`
        if (!ordered.includes(label)) {
          ordered.push(label)
        }
      }
      if (ordered.length === 0) {
        ordered.push(socketBaseLabel)
      }
      return ordered
    } catch (e) {
      return [socketBaseLabel]
    }
  })()

  const tournamentSlugForWSPath = initialData?.tournament?.slug
  const roundSlugForWSPath = initialData?.round?.seq

  const getPathAdditions = (path, socketLabel) => {
    let label = socketLabel
    let seq = roundSlugForWSPath
    if (typeof socketLabel === 'string' && socketLabel.indexOf(':') !== -1) {
      const parts = socketLabel.split(':')
      label = parts[0]
      seq = parts[1]
    }
    let p = path
    if (tournamentSlugForWSPath !== undefined) {
      p += `${tournamentSlugForWSPath}/`
    }
    if (seq !== undefined) {
      p += `round/${seq}/`
    }
    p = `${p + label}/`
    return p
  }

  const handleSocketReceive = (_socketLabel, payload) => {
    store.receiveUpdatedupdateDebatesOrPanelsAttribute(payload)
  }

  const { bridges } = useWebSocket({
    sockets,
    tournamentSlugForWSPath,
    roundSlugForWSPath,
    getPathAdditions,
    handleSocketReceive,
  })

  watchEffect(() => {
    const bridge = bridges[sockets[0]]
    if (bridge) {
      store.setupWebsocketBridge(bridge)
    }
  })

  const allDebatesOrPanels = computed(() => store.allDebatesOrPanels)
  const sortedDebatesOrPanels = computed(() => store.sortedDebatesOrPanels)
  const debatesOrPanelsCount = computed(() => Object.keys(allDebatesOrPanels.value).length)

  const unallocatedItems = computed(() => {
    const allocatedItemIDs = []
    for (const [, debateOrPanel] of Object.entries(allDebatesOrPanels.value)) {
      allocatedItemIDs.push(...getUnallocatedItemFromDebateOrPanel(debateOrPanel))
    }

    const items = []
    for (const [id, item] of Object.entries(store.allocatableItems)) {
      if (!allocatedItemIDs.includes(Number(id))) {
        items.push(item)
      }
    }

    return items
  })

  return {
    store,
    sockets,
    allDebatesOrPanels,
    sortedDebatesOrPanels,
    debatesOrPanelsCount,
    unallocatedItems,
  }
}
