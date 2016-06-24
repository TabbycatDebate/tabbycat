<template>

  <div class="container-fluid">
    <div class="col-md-6">
      <div class="alert alert-warning small" role="alert">
        <span class="glyphicon glyphicon-refresh spinning"></span><strong> Loading conflicts data...</strong>
      </div>
    </div>
    <div class="col-md-6">
      <div class="alert alert-warning small" role="alert">
        <span class="glyphicon glyphicon-refresh spinning"></span><strong> Loading history data...</strong>
      </div>
    </div>
  </div>

  <div class="panel panel-default" id="tableContainer{{ table_index }}">
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

  <unallocated-adjudicators
    :adjudicators="unusedAdjudicators">
  </unallocated-adjudicators>

</template>

<script>
import SmartTable from '../tables/Table.vue'
import UnallocatedAdjudicators from './UnallocatedAdjudicators.vue'

export default {
  components: {
    SmartTable, UnallocatedAdjudicators
  },
  props: {
    adjudicators: Array,
    tableData: Object // Passed down from main.js
  },
  computed: {
    unusedAdjudicators: function () {
      return this.adjudicators.filter(function (adj) {
        return adj.debate === null;
      })
    }
  }

}

</script>