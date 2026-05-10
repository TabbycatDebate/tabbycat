export function useSortableHeader ({ sortKey, sortOrder, emit }) {
  const resort = (key) => {
    emit('resort', key)
  }

  const sortClasses = (key) => {
    const baseCSS = 'vue-sort-key '
    if (String(sortKey.value).toLowerCase() === String(key).toLowerCase()) {
      if (sortOrder.value === 'asc') {
        return `${baseCSS}vue-sort-active sort-by-asc`
      }
      return `${baseCSS}vue-sort-active sort-by-desc`
    }
    return `${baseCSS}text-muted`
  }

  return {
    resort,
    sortClasses,
  }
}
