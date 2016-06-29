<template>

  <div>

    <allocation-actions
      :regions="regions" :categories="categories"></allocation-actions>

    <div class="panel panel-default" :id="'tableContainer' + table_index">
      <div class="panel-body">
        <debate v-for="debate in debates"
          :debate="debate"
          :aff="teams[debate.aff_team]"
          :neg="teams[debate.neg_team]"
          :all-adjudicators="adjudicators">
        </debate>
      </div>
    </div>

    <unallocated-adjudicators
      :adjudicators="adjudicators"
      :current-conflict-highlights="currentConflictHighlights"
      :current-histories-highlights="currentHistoriesHighlights">
    </unallocated-adjudicators>

  </div>

</template>

<script>
import Debate from './Debate.vue'
import AllocationActions from './AllocationActions.vue'
import UnallocatedAdjudicators from './UnallocatedAdjudicators.vue'

export default {
  components: {
    AllocationActions, Debate, UnallocatedAdjudicators
  },
  props: {
    debates: Array,
    adjudicators: Object,
    teams: Object,
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
  events: {
    'set-conflicts': function (conflicts_dict) {
      // this.currentConflictHighlights = conflicts_dict;
    },
    'unset-conflicts': function () {
      // this.currentConflictHighlights = null;
    },
    'set-histories': function (histories_dict) {
      // this.currentHistoriesHighlights = histories_dict;
    },
    'unset-histories': function () {
      // this.currentConflictHighlights = null;
    }
  }

}

</script>