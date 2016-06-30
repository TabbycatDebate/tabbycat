<template>
  <div>

    <allocation-actions
      :regions="regions" :categories="categories"></allocation-actions>

    <div class="col-md-12">
      <div class="row flex-horizontal subtitle">
        <div class="thead flex-cell" data-toggle="tooltip" title="Debate Bracket">
          <span class="glyphicon glyphicon-stats"></span>
        </div>
        <div class="thead flex-cell importance-container" data-toggle="tooltip" title="More important debates receive better panels by the auto allocator">
          <span>Importance</span>
        </div>
        <div class="thead flex-1">Aff</div>
        <div class="thead flex-1">Neg</div>
        <div class="thead flex-8 flex-horizontal">
          <div class="flex-1 text-center">Chair</div>
          <div class="flex-2 text-center">Panelists</div>
          <div class="flex-2 text-center">Trainees</div>
        </div>
        <div class="thead flex-cell" data-toggle="tooltip" title="Average score of the voting majority (assumes top adjs in majority)">
          <span class="glyphicon glyphicon-stats"></span>
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