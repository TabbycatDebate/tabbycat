import { computed, ref, watch } from 'vue'
import _ from 'lodash'

export function useSortableTable ({ headers, sortableData, getSortableProperty, defaultSortKey, defaultSortOrder, externalFilterKey }) {
  const sortKey = ref(defaultSortKey || '')
  const sortOrder = ref(defaultSortOrder || '')
  const filterKey = ref('')

  // Earlier column sorts remain tie-breakers when the primary column changes.
  const sortHistory = ref([])
  watch([sortKey, sortOrder], ([key, order]) => {
    const normalizedKey = String(key || '').toLowerCase()
    sortHistory.value = normalizedKey
      ? [{ key: normalizedKey, order }, ...sortHistory.value.filter(item => item.key !== normalizedKey)]
      : []
  }, { immediate: true, flush: 'sync' })

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

    const criteria = sortHistory.value.map(item => ({
      ...item,
      index: _.findIndex(headers.value, head => String(head.key).toLowerCase() === item.key),
    })).filter(item => item.index !== -1)
    return sortableData.value.slice(0).sort((a, b) => {
      for (const { index, order } of criteria) {
        const aCellData = getSortableProperty(a, index)
        const bCellData = getSortableProperty(b, index)
        let comparison = 0
        if (aCellData === '' && bCellData === '') {
          comparison = 0
        } else if (aCellData === '') {
          comparison = 1
        } else if (bCellData === '') {
          comparison = -1
        } else if (_.isString(aCellData) || _.isString(bCellData)) {
          comparison = String(aCellData).localeCompare(String(bCellData), undefined, { sensitivity: 'base' })
        } else {
          comparison = Number(aCellData) - Number(bCellData)
        }
        if (comparison) {
          return order === 'desc' ? -comparison : comparison
        }
      }
      return 0
    })
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
    sortHistory,
    filterKey,
    updateSorting,
    dataOrderedByKey,
    dataFilteredByKey,
  }
}
