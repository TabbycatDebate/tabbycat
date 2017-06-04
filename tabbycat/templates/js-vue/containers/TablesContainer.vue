<template>

  <div>

    <div class="row">
      <div class="col-md-12 half-vertical-spacing hidden-print">
        <div class="input-group">
          <input id="table-search" type="search"
                 v-model="filterKey" v-on:keyup="updateTableFilters"
                 class="form-control table-search" placeholder="Find in Table">
          <span class="input-group-addon">
            <span class="glyphicon glyphicon-search"></span>
          </span>
        </div>
      </div>
    </div>

    <div class="row">
      <div v-for="(table, i) in tablesData" :class="tableClass">
        <div class="panel panel-default table-container" :id="getTableId(i)">
          <div class="panel-heading" v-if="table.title">
            <h4 class="panel-title">{{ table.title }}</h4>
          </div>
          <div class="panel-body">
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

  </div>

</template>

<script>
import SmartTable from '../tables/SmartTable.vue'

export default {
  components: {
    SmartTable
  },
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
  },
  methods: {
    getTableId: function(i) {
      return "tableContainer-" + i
    },
    updateTableFilters: function() {
      this.$eventHub.$emit('update-table-filters', this.filterKey)
    }
  },
}

</script>
