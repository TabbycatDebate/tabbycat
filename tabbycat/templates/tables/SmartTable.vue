<script setup>
import _ from 'lodash'
import { mkConfig, generateCsv, download } from 'export-to-csv'
import { computed, defineAsyncComponent, toRef } from 'vue'
import SmartHeader from './SmartHeader.vue'
import SmartCell from './SmartCell.vue'
import CheckCell from '../tables/CheckCell.vue'
import BallotsCell from '../../results/templates/BallotsCell.vue'
import { useSortableTable } from '../composables/useSortableTable.js'

const FeedbackTrend = defineAsyncComponent(() => import('../graphs/FeedbackTrend.vue'))

const props = defineProps({
  tableHeaders: Array,
  tableContent: Array,
  tableClass: String,
  emptyTitle: String,
  highlightColumn: Number, // Column index to use for row highlighting (null/undefined = no highlighting)
  defaultSortKey: {
    type: String,
    default: '',
  },
  defaultSortOrder: {
    type: String,
    default: '',
  },
  externalFilterKey: String,
})

const emit = defineEmits(['toggle-checked'])

const rows = computed(() => {
  const rows = []
  for (let i = 0; i < props.tableContent.length; i += 1) {
    const rowCells = []
    for (let j = 0; j < props.tableContent[i].length; j += 1) {
      rowCells.push(props.tableContent[i][j])
    }
    rows.push(rowCells)
  }
  return rows
})

const headers = computed(() => {
  const headers = []
  if (typeof (props.tableContent[0]) !== 'undefined') {
    for (let i = 0; i < props.tableHeaders.length; i += 1) {
      headers.push(props.tableHeaders[i])
    }
  }
  return headers
})

const sortableData = computed(() => rows.value)

const getSortableProperty = (row, orderedHeaderIndex) => {
  const cell = row[orderedHeaderIndex]
  const cellData = _.isUndefined(cell.sort) ? cell.text : cell.sort
  return cellData
}

const {
  sortKey,
  sortOrder,
  updateSorting,
  dataFilteredByKey,
} = useSortableTable({
  headers,
  sortableData,
  getSortableProperty,
  defaultSortKey: props.defaultSortKey,
  defaultSortOrder: props.defaultSortOrder,
  externalFilterKey: toRef(props, 'externalFilterKey'),
})

const getCellDataWithHighlight = (cellData, _cellIndex, rowIndex) => {
  if (props.highlightColumn != null && rowIndex > 0) {
    const currentRow = dataFilteredByKey.value[rowIndex]
    const previousRow = dataFilteredByKey.value[rowIndex - 1]
    const currentValue = getSortableProperty(currentRow, props.highlightColumn)
    const previousValue = getSortableProperty(previousRow, props.highlightColumn)
    if (currentValue !== previousValue) {
      const modifiedCellData = { ...cellData }
      const existingClass = modifiedCellData.class || ''
      modifiedCellData.class = existingClass ? `${existingClass} highlight-row` : 'highlight-row'
      return modifiedCellData
    }
  }
  return cellData
}

const copyTableData = async () => {
  const content = props.tableContent.map(row =>
    row.reduce((acc, cell, index) => {
      acc[props.tableHeaders[index].key] = (cell.text ? cell.text.replace(/<[^>]*>?/gm, '') : '')
      return acc
    }, {}),
  )
  const csvConfig = mkConfig({ useKeysAsHeaders: true })
  const csvData = generateCsv(csvConfig)(content)
  await navigator.clipboard.writeText(csvData)
}

defineExpose({ copyTableData })

const componentMap = {
  SmartCell,
  'check-cell': CheckCell,
  'ballots-cell': BallotsCell,
  'feedback-trend': FeedbackTrend,
}

const resolveCellComponent = (cellData) => {
  return componentMap[cellData.component] ?? SmartCell
}
</script>

<template>
  <div class="table-responsive-md">
    <table
      class="table"
      :class="tableClass"
    >
      <thead>
        <tr>
          <smart-header
            v-for="header in headers"
            :key="header.key"
            :header="header"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            @resort="updateSorting"
          />
        </tr>
      </thead>

      <tbody>
        <tr v-if="typeof tableHeaders === 'undefined' || rows.length === 0">
          <td class="empty-cell text-center text-muted">
            {{ emptyTitle }}
          </td>
        </tr>
        <tr v-for="(row, rowIndex) in dataFilteredByKey">
          <component
            :is="resolveCellComponent(cellData)"
            v-for="(cellData, cellIndex) in row"
            :key="cellIndex"
            :cell-data="getCellDataWithHighlight(cellData, cellIndex, rowIndex)"
            @toggle-checked="emit('toggle-checked', $event)"
          />
        </tr>
      </tbody>
    </table>
  </div>
</template>
