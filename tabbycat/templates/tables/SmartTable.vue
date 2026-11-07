<script setup>
import _ from 'lodash'
import { mkConfig, generateCsv, download } from 'export-to-csv'
import { computed, defineAsyncComponent, onBeforeUnmount, ref, toRef, watch } from 'vue'
import SmartHeader from './SmartHeader.vue'
import SmartCell from './SmartCell.vue'
import CheckCell from '../tables/CheckCell.vue'
import AjaxSelectCell from '../tables/AjaxSelectCell.vue'
import BallotsCell from '../../results/templates/BallotsCell.vue'
import { useCheckboxSelection } from '../composables/useCheckboxSelection.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'
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
  defaultSortHistory: {
    type: Array,
    default: () => [],
  },
  externalFilterKey: String,
})

const emit = defineEmits(['saved', 'toggle-checked'])

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

const getCellValue = (cell) => {
  if (cell.component === 'ajax-select-cell') {
    return cell.value ?? ''
  }
  if (cell.component === 'check-cell') {
    return cell.checked ?? false
  }
  return _.isUndefined(cell.sort) ? cell.text : cell.sort
}

const getSortableProperty = (row, orderedHeaderIndex) => {
  const cell = row[orderedHeaderIndex]
  return getCellValue(cell)
}

const {
  sortKey,
  sortOrder,
  sortHistory,
  updateSorting,
  getRowKey,
  dataFilteredByKey,
} = useSortableTable({
  headers,
  sortableData,
  getSortableProperty,
  defaultSortKey: props.defaultSortKey,
  defaultSortOrder: props.defaultSortOrder,
  defaultSortHistory: props.defaultSortHistory,
  externalFilterKey: toRef(props, 'externalFilterKey'),
})

const { gettext } = useDjangoI18n()
const { selected, start, extend, stop, clear } = useCheckboxSelection()
const tableElement = ref(null)
const cellRefs = new Map()
const dragging = ref(false)
let gesture = null
let suppressClick = false

const hasCheckboxes = computed(() => rows.value.some(row => row.some(cell => cell.component === 'check-cell')))

const isHighlightedRow = (rowIndex) => props.highlightColumn != null && rowIndex > 0 &&
  getSortableProperty(dataFilteredByKey.value[rowIndex], props.highlightColumn) !==
  getSortableProperty(dataFilteredByKey.value[rowIndex - 1], props.highlightColumn)

const setCellRef = (cell, instance) => {
  if (instance) cellRefs.set(cell, instance)
  else cellRefs.delete(cell)
}

const getPosition = (target) => {
  const cell = target?.closest('td[data-row]')
  if (!cell || cell.closest('table') !== tableElement.value) return null
  return { row: Number(cell.dataset.row), column: Number(cell.dataset.column) }
}

const moveSelection = (event) => {
  if (!gesture || event.pointerId !== gesture.id) return
  if (!dragging.value && Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y) < 5) return
  dragging.value = true
  event.preventDefault()
  const position = getPosition(document.elementFromPoint(event.clientX, event.clientY))
  if (position) extend(position.row, position.column)
}

const finishSelection = (event) => {
  if (!gesture || (event && event.pointerId !== gesture.id)) return
  suppressClick = dragging.value
  if (dragging.value) tableElement.value?.focus({ preventScroll: true })
  dragging.value = false
  gesture = null
  stop()
  window.removeEventListener('pointermove', moveSelection)
  window.removeEventListener('pointerup', finishSelection)
  window.removeEventListener('pointercancel', cancelSelection)
  window.removeEventListener('blur', cancelSelection)
}

const cancelSelection = () => {
  finishSelection()
  clear()
}

const beginSelection = (event) => {
  if (event.button !== 0 || event.pointerType !== 'mouse') return
  suppressClick = false
  const position = getPosition(event.target)
  if (!position) return
  const cell = dataFilteredByKey.value[position.row][position.column]
  if (cell.component !== 'check-cell' || cell.disabled) return
  start(dataFilteredByKey.value, position.row, position.column)
  gesture = { id: event.pointerId, x: event.clientX, y: event.clientY }
  window.addEventListener('pointermove', moveSelection, { passive: false })
  window.addEventListener('pointerup', finishSelection)
  window.addEventListener('pointercancel', cancelSelection)
  window.addEventListener('blur', cancelSelection)
}

const preventDragClick = (event) => {
  if (suppressClick) {
    event.preventDefault()
    event.stopPropagation()
    suppressClick = false
  }
}

const setSelected = (checked, keepSelection = false) => {
  const changedTypes = new Map()
  for (const cell of selected.value) {
    if (cell.checked === checked || cell.disabled) continue
    cellRefs.get(cell)?.checkUpdate(checked, false)
    if (!cell.noSave && cell.saveURL === undefined) changedTypes.set(cell.type, cell)
  }
  for (const cell of changedTypes.values()) emit('toggle-checked', cell)
  if (!keepSelection) clear()
}

const toggleSelectedWithSpace = (event) => {
  if (!selected.value.size || (event.target !== tableElement.value &&
    !event.target.matches('input[type="checkbox"]'))) return
  event.preventDefault()
  if (!event.repeat) {
    const checkAll = [...selected.value].some(cell => !cell.disabled && !cell.checked)
    setSelected(checkAll, true)
  }
}

watch(() => [props.externalFilterKey, sortHistory.value, props.tableContent], cancelSelection)
onBeforeUnmount(cancelSelection)

const copyTableData = async () => {
  // Reuse one detached element while decoding the table's cells.
  const decoder = document.createElement('textarea')
  const getPlainText = (html) => {
    decoder.innerHTML = html.replace(/<[^>]*>?/gm, '')
    return decoder.value
  }
  const content = props.tableContent.map(row =>
    row.reduce((acc, cell, index) => {
      const value = cell.export ?? (['ajax-select-cell', 'check-cell'].includes(cell.component)
        ? getCellValue(cell)
        : cell.text)
      acc[props.tableHeaders[index].key] = typeof value === 'string'
        ? getPlainText(value)
        : (value ?? '')
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
  'ajax-select-cell': AjaxSelectCell,
  'ballots-cell': BallotsCell,
  'feedback-trend': FeedbackTrend,
}

const resolveCellComponent = (cellData) => {
  return componentMap[cellData.component] ?? SmartCell
}
</script>

<template>
  <div @keydown.space.capture="toggleSelectedWithSpace">
    <div
      v-if="hasCheckboxes"
      class="checkbox-selection-tools mb-2 d-print-none"
    >
      <small
        v-if="!selected.size"
        class="text-muted"
      >
        {{ gettext('Drag across checkbox cells to select a range.') }}
      </small>
      <div
        v-else
        class="d-flex align-items-center"
        role="group"
        :aria-label="gettext('Selected checkboxes')"
      >
        <span
          class="mr-2"
          aria-live="polite"
        >{{ selected.size }} {{ gettext('selected') }} — {{ gettext('Space to toggle') }}</span>
        <button
          type="button"
          class="btn btn-sm btn-primary mr-2"
          @click="setSelected(true)"
        >
          {{ gettext('Check selected') }}
        </button>
        <button
          type="button"
          class="btn btn-sm btn-primary mr-2"
          @click="setSelected(false)"
        >
          {{ gettext('Uncheck selected') }}
        </button>
        <button
          type="button"
          class="btn btn-sm btn-light"
          @click="clear"
        >
          {{ gettext('Clear selection') }}
        </button>
      </div>
    </div>
    <div class="table-responsive-md">
      <table
        ref="tableElement"
        tabindex="-1"
        class="table"
        :class="[tableClass, { 'checkbox-dragging': dragging, 'has-checkbox-selection': selected.size > 0 }]"
        @pointerdown="beginSelection"
        @click.capture="preventDragClick"
        @keydown.esc="cancelSelection"
      >
        <thead>
          <tr>
            <smart-header
              v-for="header in headers"
              :key="header.key"
              :header="header"
              :sort-key="sortKey"
              :sort-order="sortOrder"
              :sort-history="sortHistory"
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
          <tr
            v-for="(row, rowIndex) in dataFilteredByKey"
            :key="getRowKey(row)"
          >
            <component
              :is="resolveCellComponent(cellData)"
              v-for="(cellData, cellIndex) in row"
              :key="cellIndex"
              :ref="instance => setCellRef(cellData, instance)"
              :cell-data="cellData"
              :data-row="rowIndex"
              :data-column="cellIndex"
              :class="{ 'highlight-row': isHighlightedRow(rowIndex), 'checkbox-selected': selected.has(cellData) }"
              @saved="emit('saved', $event)"
              @toggle-checked="emit('toggle-checked', $event)"
            />
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.checkbox-selection-tools {
  min-height: 2rem;
  display: flex;
  align-items: center;
}
.checkbox-dragging {
  user-select: none;
}
.table.has-checkbox-selection:focus {
  outline: none;
}
.table :deep(td.checkbox-selected input[type="checkbox"]) {
  outline: 3px auto #005fcc;
  outline-offset: 3px;
}
</style>
