<script>
// Controller for calculating and setting conflicts and history highlights
// Inheriting classes can overide conflictableTeams() / conflictableAdjudicators()
// to return subsets of teams/adjs to check for
// Each must handle settingunsetting currentHistories/currentConflicts props

export default {
  props: {
    currentConflicts: {default: null },
    currentHistories: {default: null }
  },
  methods: {
    getConflictableTeams: function() {
      return this.teams;
    },
    getConflictableAdjudicators: function() {
      return this.adjudicators;
    },
    findIndividualConflict: function(conflictables, conflictedID, type, value) {
      // For each known conflict, check if ID is in the list of conflictables
      var conflictMatch = conflictables[conflictedID];
      if (typeof conflictMatch !== 'undefined') {
        conflictMatch[type] = value
      }
    },
    findMatchingInstitutionalConflict: function(conflictables, institutionID, type, value) {
      // Loop through all possible conflictables and check for institutional ID matches
      for (var referenceToTest in conflictables) {
        if (conflictables.hasOwnProperty(referenceToTest)) {
          var entityToTest = conflictables[referenceToTest]; // get team or adj
          if (typeof entityToTest !== 'undefined') {
            if (entityToTest.institution.id === institutionID) {
              entityToTest.hasInstitutionalConflict = value;
            }
          }
        }
      }
    },
    findMatchingConflicts: function(conflicts, conflictables, type, value, isInstitutional) {
      // Loop through all conflicts; dispatch to Individual/Institutional
      var _this = this;
      if (typeof conflicts !== 'undefined' && conflicts.length > 0) {
        conflicts.forEach(function(conflictedID) {
          if (isInstitutional === false) {
            _this.findIndividualConflict(conflictables, conflictedID, type, value)
          } else if (isInstitutional === true) {
            _this.findMatchingInstitutionalConflict(conflictables, conflictedID, type, value)
          }
        })
      }
    },
    toggleConflictsValues: function(conflictValue) {
      var conflicts = this.currentConflicts;
      var conflictableTeams = this.getConflictableTeams()
      var conflictableAdjudicators = this.getConflictableAdjudicators()

      if (typeof conflicts !== 'undefined') {

        this.findMatchingConflicts(conflicts.personal_adjudicators,
          conflictableAdjudicators, 'hasPersonalConflict', conflictValue, false)

        this.findMatchingConflicts(conflicts.personal_teams,
          conflictableTeams, 'hasPersonalConflict', conflictValue, false)

        this.findMatchingConflicts(conflicts.institutional_conflicts,
          conflictableAdjudicators, 'hasInstitutionalConflict', conflictValue, true)

        this.findMatchingConflicts(conflicts.institutional_conflicts,
          conflictableTeams, 'hasInstitutionalConflict', conflictValue, true)

        // Don't highlight current thing being hovered
        conflicts.currentOrigin.hasPersonalConflict = false;
        conflicts.currentOrigin.hasInstitutionalConflict = false;
      }
    },
    toggleHistoriesValues: function(historyValue) {
      // For each entry in the currently-hovered adj/team step through it and
      // set hasHistory/historyRoundsAgo values for each adj/team affected
      var histories = this.currentHistories;
      var conflictableAdjudicators = this.getConflictableAdjudicators()
      var conflictableTeams = this.getConflictableTeams()

      if (typeof histories !== 'undefined') {
        if (histories.length > 0) {
          histories.forEach(function(history) {
            if (typeof history.team !== 'undefined') {
              var team = conflictableTeams[history.team]
              if (typeof team !== 'undefined') {
                team.hasHistoryConflict = historyValue;
                if (history.ago < team.historyRoundsAgo) {
                  team.historyRoundsAgo = history.ago;
                }
              }
            } else if (typeof history.adjudicator !== 'undefined') {
              var adjudicator = conflictableAdjudicators[history.adjudicator]
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
    }
  }
}
</script>
