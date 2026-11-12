<script setup>
import SmartTable from './SmartTable.vue'
import SearchInput from '../components/SearchInput.vue'
import { computed, onUnmounted, ref } from 'vue'
import AutoSaveCounter from '../allocations/AutoSaveCounter.vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  tablesData: Array, // Passed down from main.js
  orientation: String, // Passed down from template
})

const emit = defineEmits(['toggle-checked'])

const { gettext } = useDjangoI18n()
const filterKey = ref('')
const lastSaved = ref(null)

const tableRefs = ref({})
const copiedTableIndex = ref(null)
let copyTimeout
onUnmounted(() => {
  clearTimeout(copyTimeout)
})

const hasAjaxSelectCells = computed(() => props.tablesData.some(table =>
  table.data.some(row => row.some(cell => cell.component === 'ajax-select-cell')),
))

const setTableRef = (i) => (el) => {
  if (el) {
    tableRefs.value[i] = el
  } else {
    delete tableRefs.value[i]
  }
}

const tableClass = computed(() => {
  if (props.tablesData.length === 1) {
    return 'col-md-12'
  }
  if (props.orientation === 'rows') {
    return 'col-md-12'
  }
  if (props.orientation === 'columns') {
    return 'col-md-6'
  }
  return 'col-md-12'
})

const getTableId = (i) => `tableContainer-${i}`

const copyTableTrigger = async (i) => {
  const child = tableRefs.value[i]
  if (!child) return
  await child.copyTableData()
  if (tableRefs.value[i] !== child) return
  clearTimeout(copyTimeout)
  copiedTableIndex.value = i
  copyTimeout = setTimeout(() => {
    copiedTableIndex.value = null
  }, 1500)
}
</script>

<template>
  <div class="row">
    <div class="col-12 mb-3 d-print-none">
      <div class="d-flex align-items-center">
        <search-input
          id="table-search"
          v-model="filterKey"
          :label="gettext('Find in Table')"
          :placeholder="gettext('Find in Table')"
        />
        <auto-save-counter
          v-if="hasAjaxSelectCells"
          class="ml-2"
          :last-saved="lastSaved"
        />
      </div>
    </div>

    <div
      v-for="(table, i) in tablesData"
      :key="i"
      class="col mb-3"
      :class="tableClass"
    >
      <div
        :id="getTableId(i)"
        class="card table-container pl-1 pl-sm-0"
      >
        <div class="card-body pl-3 pr-0 pr-sm-3 py-2">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h4
              v-if="table.title"
              class="card-title my-0"
            >
              {{ table.title }}
              <small
                v-if="table.subtitle"
                class="text-muted d-md-inline d-none"
              >
                {{ table.subtitle }}
              </small>
            </h4>
            <div
              class="d-flex align-items-center ml-auto mr-3 mr-sm-0 d-print-none"
            >
              <span
                class="small text-success mr-2"
                role="status"
              >{{ copiedTableIndex === i ? gettext('Copied!') : '' }}</span>
              <button
                class="btn btn-light btn-sm border p-1"
                type="button"
                data-toggle="tooltip"
                data-trigger="hover focus"
                :title="gettext('Copy table data to clipboard in a CSV format')"
                :aria-label="gettext('Copy table data to clipboard')"
                @click="copyTableTrigger(i)"
              >
                <i
                  data-feather="clipboard"
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>
          <smart-table
            :ref="setTableRef(i)"
            :table-headers="table.head"
            :table-content="table.data"
            :table-class="table.class"
            :default-sort-key="table.sort_key"
            :default-sort-order="table.sort_order"
            :default-sort-history="table.sort_history"
            :empty-title="table.empty_title"
            :highlight-column="table.highlight_column"
            :external-filter-key="filterKey"
            @saved="lastSaved = $event"
            @toggle-checked="emit('toggle-checked', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
