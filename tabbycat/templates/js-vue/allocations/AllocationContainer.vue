<template>

  <allocation-actions
    :regions="regions" :categories="categories"></allocation-actions>

  <div class="col-md-12">
    <div class="row flex-horizontal subtitle">
      <div class="col-md-1">Bracket</div>
      <div class="col-md-1 ">Importance</div>
      <div class="col-md-1">Aff</div>
      <div class="col-md-1">Neg</div>
      <div class="col-md-8 flex-horizontal ">
        <div class="flex-1">Chair</div>
        <div class="flex-1">Panelists</div>
        <div class="flex-1">Trainees</div>
      </div>
    </div>
    <debate v-for="debate in debates"
      :debate="debate"
      :aff="teams[debate.aff_team]"
      :neg="teams[debate.neg_team]"
      :all-adjudicators="adjudicators">
    </debate>
  </div>

  <unallocated-adjudicators
    :adjudicators="adjudicators"
    :current-conflict-highlights="currentConflictHighlights"
    :current-histories-highlights="currentHistoriesHighlights">
  </unallocated-adjudicators>

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