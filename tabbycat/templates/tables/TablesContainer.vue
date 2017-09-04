<template>
  <div class="row">

    <div class="col-12 mb-1 hidden-print">
      <div class="input-group">
        <input class="form-control" id="table-search" type="search"
               v-model="filterKey" @keyup="updateTableFilters"
               placeholder="Find in Table">
        <span class="input-group-addon">
          <i data-feather="search"></i>
        </span>
      </div>
    </div>

    <div class="col" v-for="(table, i) in tablesData" :class="tableClass">
      <div class="card" :id="getTableId(i)">
        <div class="card-body table-container">
          <h4 class="card-title p-2" v-if="table.title">{{ table.title }}</h4>
          <smart-table
            :table-headers="table.head" :table-content="table.data"
            :table-class="table.class"
            :default-sort-key="table.sort_key"
            :default-sort-order="table.sort_order">
          </smart-table>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import SmartTable from './SmartTable.vue'

export default {
  components: {SmartTable},
  props: {
    tablesData: Array, // Passed down from main.js
    orientation: String, // Passed down from template
  },
  data: function() {
    return { filterKey: '' } // Filter key is internal state
  },
  computed: {
    tableClass: function () {
      if (this.tablesData.length === 1) {
        return 'col-md-12';
      } else {
        if (this.orientation === "rows") {
          return 'col-md-12';
        }
        if (this.orientation === "columns") {
          return 'col-md-6';
        }
      }
      return 'col-md-12'; // Fallback; should be redundant
    },
    sortableData: function() {
      return this.rows // Enables SortableTableMixin
    }
  },
  methods: {
    getTableId: function(i) {
      return "tableContainer-" + i
    },
    updateTableFilters: function() {
      this.$eventHub.$emit('update-table-filters', this.filterKey)
    },
  },
}
</script>
