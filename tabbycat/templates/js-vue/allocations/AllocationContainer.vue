<template>
  <div>

    <allocation-actions
      :regions="regions" :categories="categories" :urls="urls">
    </allocation-actions>

    <div class="col-md-12 allocation-container">
      <div class="row flex-horizontal subtitle">
        <div class="thead flex-cell text-center" data-toggle="tooltip" title="Debate Bracket">
          <span class="glyphicon glyphicon-stats"></span>
        </div>
        <div class="thead flex-cell text-center" data-toggle="tooltip" title="How many teams are live in this room">
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
          <div class="flex-2 text-center">Panelists</div>
          <div class="flex-1 text-center">Trainees</div>
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
      :adjudicators="unallocatedAdjudicators">
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
    unallocatedAdjudicators: function() {
      // Look through all debate's panels, check for adjudicator's ID
      var unAllocatedAdjudicators = []
      var allocatedIDs = []
      for (var i = 0, dlen = this.debates.length; i < dlen; i++) {
        for (var j = 0, plen = this.debates[i].panel.length; j < plen; j++) {
          allocatedIDs.push(this.debates[i].panel[j].id)
        }
      }
      // From this list identify adjs not present in a panel
      for (var property in this.adjudicators) {
        if (this.adjudicators.hasOwnProperty(property)) {
          if (allocatedIDs.indexOf(Number(property)) === -1) {
            unAllocatedAdjudicators.push(this.adjudicators[property])
          }
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
    }
  },
  methods: {
    toggleConflictsValues: function(conflictValue) {
      var conflicts = this.currentConflictHighlights;
      var _this = this;
      if (typeof conflicts !== 'undefined) {
        if (typeof conflicts.personal_adjudicators !== 'undefined') {
          if (conflicts.personal_adjudicators.length > 0) {
            conflicts.personal_adjudicators.forEach(function(currentValue) {
              var adjudicator = _this.adjudicators[currentValue];
              if (typeof adjudicator !== 'undefined') {
                adjudicator.hasPersonalConflict = conflictValue
              }
            })
          }
        }
        if (typeof conflicts.personal_teams !== 'undefined') {
          if (conflicts.personal_teams.length > 0) {
            conflicts.personal_teams.forEach(function(currentValue) {
              var team = _this.teams[currentValue];
              if (typeof team !== 'undefined') {
                team.hasPersonalConflict = conflictValue
              }
            })
          }
        }
        if (typeof conflicts.institutional_conflicts !== 'undefined') {
          if (conflicts.institutional_conflicts.length > 0) {
            conflicts.institutional_conflicts.forEach(function(currentValue) {
              // Loop through all adjudicators
              for (var adjudicatorID in _this.adjudicators) {
                if (_this.adjudicators.hasOwnProperty(adjudicatorID)) {
                  var adjToTest = _this.adjudicators[adjudicatorID];
                  if (typeof adjToTest !== 'undefined' && adjToTest.institution.id === currentValue) {
                    adjToTest.hasInstitutionalConflict = conflictValue;
                  }
                }
              }
              // Loop through all teams
              for (var teamID in _this.teams) {
                if (_this.teams.hasOwnProperty(teamID)) {
                  var teamToTest = _this.teams[teamID];
                  if (typeof teamToTest !== 'undefined' && teamToTest.institution.id === currentValue) {
                    teamToTest.hasInstitutionalConflict = conflictValue;
                  }
                }
              }
            });
          }
        }
        // Don't highlight current thing being hovered
        conflicts.currentOrigin.hasPersonalConflict = false;
        conflicts.currentOrigin.hasInstitutionalConflict = false;
      }
    },
    toggleHistoriesValues: function(historyValue) {
      // For each entry in the currently-hovered adj/team step through it and
      // set hasHistory/historyRoundsAgo values for each adj/team affected
      var histories = this.currentHistoriesHighlights;
      if (histories.length > 0) {
        var _this = this;
        histories.forEach(function(history) {
          if (typeof history.team !== 'undefined') {
            var team = _this.teams[history.team]
            if (typeof team !== 'undefined') {
              team.hasHistoryConflict = historyValue;
              if (history.ago < team.historyRoundsAgo) {
                team.historyRoundsAgo = history.ago;
              }
            }
          } else if (typeof history.adjudicator !== 'undefined') {
            var adjudicator = _this.adjudicators[history.adjudicator]
            if (typeof adjudicator !== 'undefined') {
              adjudicator.hasHistoryConflict = historyValue;
              if (history.ago < adjudicator.historyRoundsAgo) {
                adjudicator.historyRoundsAgo = history.ago;
              }
            }
          }
        });
      }
    }
  },
  events: {
    'set-conflicts': function (conflicts_dict) {
      this.currentConflictHighlights = conflicts_dict;
      this.toggleConflictsValues(true);
    },
    'unset-conflicts': function () {
      this.toggleConflictsValues(false);
      this.currentConflictHighlights = null;
    },
    'set-histories': function (histories_dict) {
      this.currentHistoriesHighlights = histories_dict;
      this.toggleHistoriesValues(true);
    },
    'unset-histories': function() {
      this.toggleHistoriesValues(false);
      this.currentConflictHighlights = null;
    },
    'set-dragged-adj': function(dragInfo) {
      this.currentlyDragging = dragInfo;
    },
    'unset-dragged-adj': function() {
      this.currentlyDragging = null;
    },
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
      this.currentlyDragging = null;
      this.toggleConflictsValues(false);
      this.currentConflictHighlights = null;
      this.toggleHistoriesValues(false);
      this.currentConflictHighlights = null;
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