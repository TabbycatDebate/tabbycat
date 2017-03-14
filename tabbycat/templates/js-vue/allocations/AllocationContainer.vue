<template>
  <div>

    <allocation-actions
      :regions="regions" :categories="categories" :round-info="roundInfo">
    </allocation-actions>

    <div class="col-md-12 allocation-container">

      <div class="vertical-spacing" id="messages-container"></div>

      <div class="row flex-horizontal subtitle">
        <div class="thead flex-cell text-center" data-toggle="tooltip" title="Debate Bracket">
          <span class="glyphicon glyphicon-stats"></span>
        </div>
        <div class="thead flex-cell text-center" data-toggle="tooltip" title="How many break categories are live in this room (across both teams)">
          <span class="glyphicon glyphicon-heart"></span>
        </div>
        <div class="thead flex-cell importance-container" data-toggle="tooltip" title="More important debates receive better panels by the auto allocator">
          <span>Importance</span>
        </div>
        <div class="thead flex-cell debate-team">Aff</div>
        <div class="thead flex-cell debate-team">Neg</div>
        <div class="thead flex-6 flex-horizontal">
          <div class="flex-cell text-center" data-toggle="tooltip" title="Average score of the voting majority (assumes top adjs in majority)">
            <span class="glyphicon glyphicon-signal"></span>
          </div>
          <div class="flex-1 text-center">Chair</div>
          <div class="flex-2 text-center">Panellists</div>
          <div class="flex-1 text-center">Trainees</div>
        </div>
      </div>

      <debate v-for="debate in debates | orderBy 'importance' -1"
        :debate="debate"
        :aff="teams[debate.aff_team]"
        :neg="teams[debate.neg_team]"
        :all-adjudicators="adjudicators"
        :round-info="roundInfo">
      </debate>

    </div>

    <unallocated-adjudicators
      :adjudicators="unallocatedAdjudicators"
      :round-info="roundInfo">
    </unallocated-adjudicators>

    <div class="modal fade" id="modalAlert" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header h4 text-danger"></div>
          <div class="modal-body"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import Debate from './Debate.vue'
import AllocationActions from './AllocationActions.vue'
import UnallocatedAdjudicators from './UnallocatedAdjudicators.vue'
import ConflictsCalculatorMixin from '../mixins/ConflictsCalculatorMixin.vue'

export default {
  components: {
    AllocationActions, Debate, UnallocatedAdjudicators
  },
  mixins: [
    ConflictsCalculatorMixin
  ],
  props: {
    debates: Array,
    adjudicators: Object,
    teams: Object,
    regions: Array,
    categories: Array,
    roundInfo: Object,
    currentlyDragging: Object
  },
  computed: {
    unallocatedAdjudicators: function() {
      // Look through all debate's panels, check for adjudicator's ID
      var unAllocatedAdjudicators = []
      var allocatedIDs = []
      for (var i = 0, dlen = this.debates.length; i < dlen; i++) {
        for (var j = 0, plen = this.debates[i].panel.length; j < plen; j++) {
          allocatedIDs.push(this.debates[i].panel[j].id)
        }
      }
      for (var property in this.adjudicators) {
        if (this.roundInfo.allowDuplicateAllocations !== true) {
          // From this list identify adjs not present in a panel
          if (this.adjudicators.hasOwnProperty(property)) {
            if (allocatedIDs.indexOf(Number(property)) === -1) {
              unAllocatedAdjudicators.push(this.adjudicators[property])
            }
          }
        } else {
          // Return all adjudicators regardless of panle assignments
          unAllocatedAdjudicators.push(this.adjudicators[property])
        }
      }
      return unAllocatedAdjudicators
    },
    debatesByID: function() {
      var lookup = {};
      for (var i = 0, len = this.debates.length; i < len; i++) {
        lookup[this.debates[i].id] = this.debates[i];
      }
      return lookup;
    },
    conflictableTeams: function() {
      return this.teams;
    },
    conflictableAdjudicators: function() {
      return this.adjudicators;
    },
  },
  events: {
    // Determine dragged object
    'set-dragged-adj': function(dragInfo) {
      this.currentlyDragging = dragInfo;
    },
    'unset-dragged-adj': function() {
      this.currentlyDragging = null;
    },
    // Determine hover conflicts
    'set-hover-conflicts': function (origin, conflicts_dict, histories_dict) {
      this.toggleConflicts(true, 'hover', origin, conflicts_dict);
      this.toggleHistories(true, 'hover', origin, histories_dict);
    },
    'unset-hover-conflicts': function (origin, conflicts_dict, histories_dict) {
      this.toggleConflicts(false, 'hover', origin, conflicts_dict);
      this.toggleHistories(false, 'hover', origin, histories_dict);
    },
    'set_diversity_highlights': function(set_state, set_type) {
      // Sets diveristy state on the original object
      // so that it will persist through drag/drops when the element is removed
      for (var adjID in this.adjudicators) {
        this.adjudicators[adjID].region_show = false
        this.adjudicators[adjID].gender_show = false
        this.adjudicators[adjID][set_type] = set_state
      }
      for (var teamID in this.teams) {
        this.teams[teamID].region_show = false
        this.teams[teamID].category_show = false
        this.teams[teamID].gender_show = false
        this.teams[teamID][set_type] = set_state
      }
    },
    // Set or unset dragg adjs to panels
    'set-adj-unused': function() {
      var adj = this.currentlyDragging.adj
      // Remove adj from any panels they came from
      if (typeof this.currentlyDragging.debateId !== 'undefined') {
        var fromDebateId = this.currentlyDragging.debateId
        var fromPanel = this.debatesByID[fromDebateId].panel
        var toRemoveIndex = fromPanel.findIndex(function(value) {
          return value.id === adj.id;
        });
        fromPanel.splice(toRemoveIndex, 1);
      }
      // Remove any highlights from hovers
      this.toggleConflicts(false, 'hover', adj, adj.conflicts);
      this.toggleHistories(false, 'hover', adj, adj.histories);
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
      // Remove any highlights from hovers
      this.toggleConflicts(false, 'hover', adj, adj.conflicts);
      this.toggleHistories(false, 'hover', adj, adj.histories);
      // Find the debate object that was dropped into and add the adj to it
      toPanel.push({'id': adj.id, 'position': toPosition})
    },
    'set-debate-panels': function(newDebatesResponse) {
      // Dispatched from the AllocationActions. Note that this.debates are props
      // in this component; not data. Need to call up to the root element to set
      this.$parent.$set('allDebates', newDebatesResponse)
      // Trigger child Debate components to recalculate conflicts
      this.$broadcast('recheck-panel-conflicts')
    }
  }

}

</script>
