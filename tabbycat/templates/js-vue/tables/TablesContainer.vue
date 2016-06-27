<template>

  <template v-for="(tableIndex, tableData) in tablesData">

    <div class="panel panel-default" id="tableContainer{{ table_index }}">
      <div class="panel-heading" v-if="tableData['title']">
        <h4 class="panel-title">{{ tableData['title'] }}</h4>
      </div>
      <div class="panel-body">
        <smart-table
          :table-headers="tableData['head']"
          :table-content="tableData['data']"
          :table-class="tableData['class']"
          :filter-key=""
          :default-sort-key="tableData['sort_key']"
          :default-sort-order="tableData['sort_order']">
        </smart-table>
      </div>
    </div>

  </template>

</template>

<script>
import SmartTable from './Table.vue'

export default {
  components: {
    SmartTable
  },
  props: {
    tablesData: Array // Passed down from main.js
  }
}

</script>