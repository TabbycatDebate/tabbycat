<template>
  <div>

    <allocation-actions
      :regions="regions" :categories="categories" :urls="urls">
    </allocation-actions>

    <div class="col-md-12 allocation-container">
      <div class="row flex-horizontal subtitle">
        <div class="thead flex-cell" data-toggle="tooltip" title="Debate Bracket">
          <span class="glyphicon glyphicon-stats"></span>
        </div>
        <div class="thead flex-1">Aff</div>
        <div class="thead flex-1">Neg</div>
        <div class="thead flex-cell importance-container" data-toggle="tooltip" title="More important debates receive better panels by the auto allocator">
          <span>Importance</span>
        </div>
        <div class="thead flex-7 flex-horizontal">
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
        :all-adjudicators="adjudicators"
        :urls="urls">
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
    urls: Object,
    currentlyDragging: Object,
    currentConflictHighlights: {default: null },
    currentHistoriesHighlights: {default: null }
  },
  computed: {
    debatesByID: function() {
      var lookup = {};
      for (var i = 0, len = this.debates.length; i < len; i++) {
        lookup[this.debates[i].id] = this.debates[i];
      }
      return lookup;
    }
  },
  events: {
    'set-conflicts': function (conflicts_dict) {
      this.currentConflictHighlights = conflicts_dict;
    },
    'unset-conflicts': function () {
      this.currentConflictHighlights = null;
    },
    'set-histories': function (histories_dict) {
      this.currentHistoriesHighlights = histories_dict;
    },
    'unset-histories': function() {
      this.currentConflictHighlights = null;
    },
    'set-dragged-adj': function(adjId) {
      this.currentlyDragging = adjId;
    },
    'unset-dragged-adj': function() {
      this.currentlyDragging = null;
    },
    'set-adj-unused': function() {
      var adj = this.currentlyDragging.adj
      adj.allocated = false
      // Remove adj from any panels they came from
      if (typeof this.currentlyDragging.debateId !== 'undefined') {
        var fromDebateId = this.currentlyDragging.debateId
        var fromPanel = this.debatesByID[fromDebateId].panel
        var toRemoveIndex = fromPanel.findIndex(function(value) {
          return value.id === adj.id;
        });
        fromPanel.splice(toRemoveIndex, 1);
      }
      this.currentlyDragging = null;
    },
    'set-adj-panel': function(toDebateId, toPosition) {
      // Construct a lookup object to find the debate by it's ID
      var adj = this.currentlyDragging.adj
      var toPanel = this.debatesByID[toDebateId].panel
      if (typeof this.currentlyDragging.debateId !== 'undefined') {
        var fromDebateId = this.currentlyDragging.debateId
        var fromPosition = this.currentlyDragging.position
        var fromPanel = this.debatesByID[fromDebateId].panel
      } else {
        var fromDebateId = false
        var fromPosition = false
      }

      // If moving to become a chair; remove/swap the current chair first
      if (toPosition === "C") {
        // Check if there is a current chair
        var currentChairIndex = toPanel.findIndex(function(value) {
          return value.position === "C";
        });
        if (currentChairIndex !== -1) {
          // If there is infact a current chair; check if we need to do a swap
          // If moving from a previous position do a swap
          if (fromDebateId !== false) {
            // Find the about to be replaced chair & add to old position
            var oldChairID = toPanel[currentChairIndex].id;
            fromPanel.push({'id': oldChairID, 'position': fromPosition});
          }
          // Remove original chair
          toPanel.splice(toRemoveIndex, 1);
        }
      }

      if (fromDebateId === false) {
        adj.allocated = true; // Triggers remove from unused area
      } else {
        var toRemoveIndex = fromPanel.findIndex(function(value) {
          return value.id === adj.id;
        });
        fromPanel.splice(toRemoveIndex, 1);
      }

      // Find the debate object that was dropped into and add the adj to it
      toPanel.push({'id': adj.id, 'position': toPosition})
      this.currentlyDragging = null;
    }
  }

}

</script>