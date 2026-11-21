import { shallowRef } from 'vue'

export function useCheckboxSelection () {
  const selected = shallowRef(new Set())
  let origin = null
  let rows = []

  const start = (visibleRows, row, column) => {
    origin = { row, column }
    rows = visibleRows.map(cells => cells.slice())
  }

  const extend = (row, column) => {
    if (!origin) return
    const cells = new Set()
    for (let r = Math.min(origin.row, row); r <= Math.max(origin.row, row); r++) {
      for (let c = Math.min(origin.column, column); c <= Math.max(origin.column, column); c++) {
        const cell = rows[r]?.[c]
        if (cell?.component === 'check-cell' && !cell.disabled) cells.add(cell)
      }
    }
    selected.value = cells
  }

  const stop = () => {
    origin = null
    rows = []
  }

  const clear = () => {
    stop()
    selected.value = new Set()
  }

  return { selected, start, extend, stop, clear }
}
