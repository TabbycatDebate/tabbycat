export function useSortableHeader ({ sortKey, sortOrder, sortHistory, emit }) {
  const resort = (key, event = {}) => {
    emit('resort', key, Boolean(event.shiftKey))
  }

  const sortPosition = (key) => {
    return (sortHistory?.value || []).findIndex(item => item.key === String(key).toLowerCase()) + 1
  }

  const sortClasses = (key) => {
    const baseCSS = 'vue-sort-key '
    const position = sortPosition(key)
    const order = position ? sortHistory.value[position - 1].order : sortOrder.value
    if (position || String(sortKey.value).toLowerCase() === String(key).toLowerCase()) {
      if (order === 'asc') {
        return `${baseCSS}vue-sort-active sort-by-asc`
      }
      return `${baseCSS}vue-sort-active sort-by-desc`
    }
    return `${baseCSS}text-muted`
  }

  const ariaSort = (key) => {
    if (sortPosition(key) !== 1) {
      return null
    }
    return sortOrder.value === 'asc' ? 'ascending' : 'descending'
  }

  return {
    resort,
    sortClasses,
    sortPosition,
    ariaSort,
  }
}
