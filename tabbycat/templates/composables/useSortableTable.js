import { computed, ref, watch } from 'vue'
import _ from 'lodash'

export function useSortableTable ({ headers, sortableData, getSortableProperty, defaultSortKey, defaultSortOrder, externalFilterKey }) {
  const sortKey = ref(defaultSortKey || '')
  const sortOrder = ref(defaultSortOrder || '')
  const filterKey = ref('')

  const updateSorting = (newSortKey) => {
    if (sortKey.value === newSortKey) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = newSortKey
      sortOrder.value = 'desc'
    }
  }

  if (externalFilterKey) {
    // externalFilterKey is a Ref (from toRef(props, 'externalFilterKey'))
    watch(externalFilterKey, (newValue) => {
      filterKey.value = newValue ?? ''
    }, { immediate: true })
  }

  const dataOrderedByKey = computed(() => {
    const key = String(sortKey.value || '').toLowerCase()
    if ((headers.value?.length ?? 0) === 0 || key === '') {
      return sortableData.value
    }

    const orderedHeaderIndex = _.findIndex(headers.value, head => String(head.key).toLowerCase() === key)
    if (orderedHeaderIndex === -1) {
      const errorDetails = `No sort key '${key}' in headers: ${_.map(headers.value, 'key')}`
      setTimeout(() => {
        throw new Error(errorDetails)
      }, 500)
      return sortableData.value
    }

    const sorted = sortableData.value.slice(0).sort((a, b) => {
      const aCellData = getSortableProperty(a, orderedHeaderIndex)
      const bCellData = getSortableProperty(b, orderedHeaderIndex)
      if (aCellData === '' || bCellData === '') {
        return -1
      }
      if (_.isString(aCellData) || _.isString(bCellData)) {
        return String(aCellData).localeCompare(String(bCellData), undefined, { sensitivity: 'base' })
      }
      return Number(aCellData) - Number(bCellData)
    })

    if (sortOrder.value === 'desc') {
      return sorted.reverse()
    }
    return sorted
  })

  const dataFilteredByKey = computed(() => {
    if (filterKey.value === '') {
      return dataOrderedByKey.value
    }
    const key = String(filterKey.value)
    if (key.length < 3) {
      return dataOrderedByKey.value
    }

    return _.filter(dataOrderedByKey.value, (row) => {
      let rowContainsMatch = false
      _.forEach(row, (cell) => {
        if (_.includes(_.lowerCase(cell?.text || ''), _.lowerCase(key))) {
          rowContainsMatch = true
        }
      })
      return rowContainsMatch
    })
  })

  return {
    sortKey,
    sortOrder,
    filterKey,
    updateSorting,
    dataOrderedByKey,
    dataFilteredByKey,
  }
}
