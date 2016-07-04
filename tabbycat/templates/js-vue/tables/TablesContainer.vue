<template>

  <div class="row">

    <div v-for="(tableIndex, tableData) in tablesData"
         v-bind:class="{'col-md-6': tablesData.length === 2,
                        'col-md-12': tablesData.length === 1}">

      <div class="panel panel-default" id="tableContainer{{ table_index }}">
        <div class="panel-heading" v-if="tableData['title']">
          <h4>{{ tableData['title'] }}</h4>
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

    </div>

  </div>

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
