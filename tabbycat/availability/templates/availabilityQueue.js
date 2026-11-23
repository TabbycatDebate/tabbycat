export function createAvailabilityQueue (cells, save, onPending, onSettled) {
  const confirmed = new Map(cells.map(cell => [cell, cell.checked]))
  const pending = new Map()
  let saving = null

  const flush = async (resolve) => {
    let failed = false
    while (pending.size) {
      const url = pending.keys().next().value.updateURL
      const batch = new Map([...pending].filter(([cell]) => cell.updateURL === url))
      for (const cell of batch.keys()) pending.delete(cell)
      const changes = Object.fromEntries([...batch].map(([cell, checked]) => [cell.id, checked]))
      try {
        await save(url, changes)
        for (const [cell, checked] of batch) confirmed.set(cell, checked)
      } catch {
        failed = true
        for (const cell of batch.keys()) {
          if (!pending.has(cell)) {
            cell.checked = confirmed.get(cell)
            cell.sort = cell.checked
          }
        }
      }
    }
    saving = null
    onSettled(!failed)
    resolve(!failed)
  }

  const enqueue = (cell) => {
    pending.set(cell, cell.checked)
    if (!saving) {
      saving = new Promise(resolve => setTimeout(flush, 50, resolve))
      onPending()
    }
  }

  return { enqueue, whenIdle: () => saving }
}
