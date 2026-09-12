export function useSortableHeader ({ sortKey, sortOrder, sortHistory, emit }) {
  const resort = (key) => {
    emit('resort', key)
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

  return {
    resort,
    sortClasses,
    sortPosition,
  }
}
