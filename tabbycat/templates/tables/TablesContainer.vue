<template>
  <div class="row">

    <div class="col-12 mb-3 hidden-print">
      <div class="input-group">
        <input id="table-search" type="search"
               v-model="filterKey" @keyup="updateTableFilters"
               class="form-control" placeholder="Find in Table">
        <span class="input-group-addon">
          <i data-feather="search"></i>
        </span>
      </div>
    </div>

    <div class="col" v-for="(table, i) in tablesData" :class="tableClass">
      <div class="card" :id="getTableId(i)">
        <div class="panel-heading" v-if="table.title">
          <h4 class="panel-title">{{ table.title }}</h4>
        </div>
        <div class="card-body table-container p-0">
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
