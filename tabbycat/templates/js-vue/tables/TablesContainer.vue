<template>

  <div>
    <div class="row">
      <div class="col-md-12 half-vertical-spacing hidden-print">
        <div class="input-group">
          <input id="table-search" type="search" v-model="filterKey"
                 class="form-control table-search" placeholder="Find in Table">
          <span class="input-group-addon">
            <span class="glyphicon glyphicon-search"></span>
          </span>
        </div>
      </div>
    </div>

    <div class="row">
      <div v-for="(tableIndex, tableData) in tablesData" v-bind:class="tableClass">
        <div class="panel panel-default table-container" v-bind:id="'tableContainer' + table_index">
          <div class="panel-heading" v-if="tableData['title']">
            <h4 class="panel-title">{{ tableData['title'] }}</h4>
          </div>
          <div class="panel-body">
            <smart-table
              :table-headers="tableData['head']"
              :table-content="tableData['data']"
              :table-class="tableData['class']"
              :filter-key="filterKey"
              :sort-key="tableData['sort_key']"
              :sort-order="tableData['sort_order'] === '' ? 'asc' : tableData['sort_order']"
            </smart-table>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import SmartTable from './Table.vue'

export default {
  components: {
    SmartTable
  },
  methods: {
    getOrSetSortOrder: function (predefinedOrder) {
      console.log(getOrSetSortOrder)
    }
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
    }
  },
  props: {
    tablesData: Array, // Passed down from main.js
    orientation: String, // Passed down from template
    filterKey: { default: '' }
  }
}

</script>
