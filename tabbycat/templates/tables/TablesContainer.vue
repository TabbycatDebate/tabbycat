<script setup>
import SmartTable from './SmartTable.vue'
import { computed, ref } from 'vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  tablesData: Array, // Passed down from main.js
  orientation: String, // Passed down from template
})

const emit = defineEmits(['toggle-checked'])

const { gettext } = useDjangoI18n()
const filterKey = ref('')

const tableRefs = ref({})

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

const copyTableTrigger = (i) => {
  const child = tableRefs.value[i]
  child?.copyTableData?.()
}
</script>

<template>
  <div class="row">
    <div class="col-12 mb-3 d-print-none">
      <div class="input-group">
        <input
          id="table-search"
          v-model="filterKey"
          class="form-control table-search"
          type="search"
          :placeholder="gettext('Find in Table')"
        >
        <div class="input-group-append">
          <span class="input-group-text"><i data-feather="search" /></span>
        </div>
        <div
          v-for="(table, i) in tablesData"
          :key="i"
        >
          <button
            class="btn btn-light border ml-2"
            data-toggle="tooltip"
            title="Copy table data to clipboard in a CSV format"
            @click.prevent="copyTableTrigger(i)"
          >
            <i data-feather="clipboard" />
          </button>
        </div>
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
        class="card table-container pl-1"
      >
        <div class="card-body pl-3 pr-0 py-2">
          <h4
            v-if="table.title"
            class="card-title mt-1 mb-2"
          >
            {{ table.title }}
            <small
              v-if="table.subtitle"
              class="text-muted d-md-inline d-none"
            >
              {{ table.subtitle }}
            </small>
          </h4>
          <smart-table
            :ref="setTableRef(i)"
            :table-headers="table.head"
            :table-content="table.data"
            :table-class="table.class"
            :default-sort-key="table.sort_key"
            :default-sort-order="table.sort_order"
            :empty-title="table.empty_title"
            :highlight-column="table.highlight_column"
            :external-filter-key="filterKey"
            @toggle-checked="emit('toggle-checked', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
