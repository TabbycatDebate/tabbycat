<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  computed: {

  },
  methods: {
    unsetAllHighlights: function() {
      this.currentlyDragging = null;
      this.toggleConflictsValues(false);
      this.currentConflictHighlights = null;
      this.toggleHistoriesValues(false);
      this.currentConflictHighlights = null;
    },
    toggleConflictsValues: function(conflictValue) {
      var conflicts = this.currentConflictHighlights;
      var _this = this;
      if (typeof conflicts !== 'undefined') {
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
    }
  }
}
</script>
