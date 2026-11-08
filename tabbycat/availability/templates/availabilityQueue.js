export function createAvailabilityQueue (cells, save, onPending, onSaved) {
  const confirmed = new Map(cells.map(cell => [cell, cell.checked]))
  const pending = new Map()
  let saving = false
  let scheduled = false

  const flush = async () => {
    scheduled = false
    if (saving) return
    saving = true
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
    saving = false
    if (!failed) onSaved()
  }

  const enqueue = (cell) => {
    pending.set(cell, cell.checked)
    onPending()
    if (!saving && !scheduled) {
      scheduled = true
      setTimeout(flush, 50)
    }
  }

  return { enqueue }
}
