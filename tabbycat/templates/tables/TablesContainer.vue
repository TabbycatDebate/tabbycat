<template>
  <div class="row">

    <div class="col-12 mb-3 d-print-none">
      <div class="input-group">
        <input class="form-control table-search" id="table-search" type="search"
               v-model="filterKey" @keyup="updateTableFilters"
               :placeholder="gettext('Find in Table')">
        <div class="input-group-append">
          <span class="input-group-text"><i data-feather="search"></i></span>
        </div>
      </div>
    </div>

    <div class="col mb-3" v-for="(table, i) in tablesData" :class="tableClass">
      <div class="card table-container pl-1" :id="getTableId(i)">
        <div class="card-body pl-3 pr-0 py-2">
          <h4 class="card-title mt-1 mb-2" v-if="table.title">
            {{ table.title }}
            <small class="text-muted d-md-inline d-none" v-if="table.subtitle">
              {{ table.subtitle }}
            </small>
          </h4>
          <smart-table
            :table-headers="table.head" :table-content="table.data"
            :table-class="table.class"
            :default-sort-key="table.sort_key"
            :default-sort-order="table.sort_order"
            :empty-title="table.empty_title">
          </smart-table>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import SmartTable from './SmartTable.vue'

export default {
  components: { SmartTable },
  props: {
    tablesData: Array, // Passed down from main.js
    orientation: String, // Passed down from template
  },
  data: function () {
    return { filterKey: '' } // Filter key is internal state
  },
  computed: {
    tableClass: function () {
      if (this.tablesData.length === 1) {
        return 'col-md-12'
      }
      if (this.orientation === 'rows') {
        return 'col-md-12'
      }
      if (this.orientation === 'columns') {
        return 'col-md-6'
      }

      return 'col-md-12' // Fallback; should be redundant
    },
    sortableData: function () {
      return this.rows // Enables SortableTableMixin
    },
  },
  methods: {
    getTableId: function (i) {
      return `tableContainer-${i}`
    },
    updateTableFilters: function () {
      this.$eventHub.$emit('update-table-filters', this.filterKey)
    },
  },
}
</script>
