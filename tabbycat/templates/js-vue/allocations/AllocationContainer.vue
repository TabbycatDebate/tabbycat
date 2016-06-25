<template>

  <allocation-actions></allocation-actions>

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

  <div class="panel panel-default" id="tableContainer{{ table_index }}">
    <div class="panel-body">
      <div class="row">
        <div class="col-md-3">
          <position-droppable
            :adjudicators="[adjudicators[0]]"
            :position="C">
          </position-droppable>
        </div>
        <div class="col-md-6">
          <position-droppable
            :adjudicators="[adjudicators[3],adjudicators[1]]"
            :position="P">
          </position-droppable>
        </div>
        <div class="col-md-3">
          <position-droppable
            :adjudicators="[adjudicators[4],adjudicators[5]]"
            :position="T">
          </position-droppable>
        </div>
      </div>
    </div>
  </div>

  <unallocated-adjudicators
    :adjudicators="unusedAdjudicators">
  </unallocated-adjudicators>

</template>

<script>
import AllocationActions from './AllocationActions.vue'
import SmartTable from '../tables/Table.vue'
import UnallocatedAdjudicators from './UnallocatedAdjudicators.vue'
import PositionDroppable from './PositionDroppable.vue'

export default {
  components: {
    AllocationActions, SmartTable, UnallocatedAdjudicators, PositionDroppable
  },
  props: {
    adjudicators: Array,
    tableData: Object // Passed down from main.js
  },
  methods: {
    moveToUnused: function(adjId) {
      var adjToMove = this.adjudidcators.filter(function( adj ) {
        return adj.id == adjId;
      });
      adjToMove.debate = null;
    }
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