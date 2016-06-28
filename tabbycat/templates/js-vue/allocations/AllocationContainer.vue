<template>

  <allocation-actions
    :regions="regions" :categories="categories"></allocation-actions>

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
        <debate-team
          v-for="team in teams"
          :team="team"
          :current-conflict-highlights="currentConflictHighlights"
          :current-histories-highlights="currentHistoriesHighlights">
        </debate-team>
      </div>
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
    :adjudicators="unusedAdjudicators"
    :current-conflict-highlights="currentConflictHighlights"
    :current-histories-highlights="currentHistoriesHighlights">
  </unallocated-adjudicators>

</template>

<script>
import DebateTeam from './DebateTeam.vue'
import AllocationActions from './AllocationActions.vue'
import SmartTable from '../tables/Table.vue'
import UnallocatedAdjudicators from './UnallocatedAdjudicators.vue'
import PositionDroppable from './PositionDroppable.vue'

export default {
  components: {
    AllocationActions, SmartTable, UnallocatedAdjudicators, PositionDroppable, DebateTeam
  },
  props: {
    adjudicators: Array,
    teams: Array,
    regions: Array,
    categories: Array,
    tableData: Object, // Passed down from main.js
    currentConflictHighlights: {default: null },
    currentHistoriesHighlights: {default: null }
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
  },
  events: {
    'set-conflicts': function (conflicts_dict) {
      this.currentConflictHighlights = conflicts_dict;
    },
    'unset-conflicts': function () {
      // this.currentConflictHighlights = null;
    },
    'set-histories': function (histories_dict) {
      this.currentHistoriesHighlights = histories_dict;
    },
    'unset-histories': function () {
      // this.currentConflictHighlights = null;
    }
  }

}

</script>