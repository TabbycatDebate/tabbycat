<script>
// Controller for calculating and setting conflicts/history highlights
// Inheriting classes should set conflictableTeams/conflictableAdjudicators
// as a computed property
// to return subsets of teams/adjs to check for
// Each must handle settingunsetting currentHistories/currentConflicts props

export default {
  methods: {
    toggleHistories: function(conflictValue, conflictState, histories) {
      if (typeof histories === 'undefined' || histories === null) {
        return
      }
      var _this = this;
      histories.forEach(function(history) {
        // Check if history conflict is for an adj or a team
        if (typeof history.team !== 'undefined') {
          var entity = _this.conflictableTeams[history.team]
        } else if (typeof history.adjudicator !== 'undefined') {
          var entity = _this.conflictableAdjudicators[history.adjudicator]
        }
        // Set history value and rounds_ago to be the lowest possible match
        if (typeof entity !== 'undefined') {
          entity.conflicted[conflictState]['history'] = conflictValue;
          if (history.ago < entity.conflicted[conflictState]['history_ago']) {
            entity.conflicted[conflictState]['history_ago'] = history.ago;
          }
        }
      });
    },
    toggleConflicts: function(conflictValue, conflictState, conflicts) {
      if (typeof conflicts === 'undefined' || conflicts === null) {
        return
      }
      this.findMatchingConflicts(conflicts.adjudicators,
        this.conflictableAdjudicators, conflictState, 'personal', conflictValue, false)
      this.findMatchingConflicts(conflicts.teams,
        this.conflictableTeams, conflictState, 'personal', conflictValue, false)
      this.findMatchingConflicts(conflicts.institutions,
        this.conflictableAdjudicators, conflictState, 'institutional', conflictValue, true)
      this.findMatchingConflicts(conflicts.institutions,
        this.conflictableTeams, conflictState, 'institutional', conflictValue, true)
    },
    findMatchingConflicts: function(conflicts, conflictables, hoverOrPanel,
      typeOfClash, isConflicted, isInstitutional) {
      // Loop through all conflicts; dispatch to Individual/Institutional
      if (typeof conflicts === 'undefined' || conflicts === null) {
        return
      }
      var _this = this;
      conflicts.forEach(function(conflictedID) {
        if (isInstitutional === false) {
          _this.findIndividualConflict(conflictables,
            conflictedID, hoverOrPanel, typeOfClash, isConflicted)
        } else if (isInstitutional === true) {
          _this.findMatchingInstitutionalConflict(conflictables,
            conflictedID, hoverOrPanel, typeOfClash, isConflicted)
        }
      })
    },
    findIndividualConflict: function(conflictables, conflictedID, hoverOrPanel, typeOfClash, isConflicted) {
      // For each known conflict, check if ID is in the list of conflictables
      var conflictMatch = conflictables[conflictedID];
      if (typeof conflictMatch !== 'undefined') {
        conflictMatch['conflicted'][hoverOrPanel][typeOfClash] = isConflicted
      }
    },
    findMatchingInstitutionalConflict: function(conflictables, institutionID, hoverOrPanel, typeOfClash, isConflicted) {
      // Loop through all possible conflictables and check for institutional ID matches
      for (var referenceToTest in conflictables) {
        if (conflictables.hasOwnProperty(referenceToTest)) {
          var entityToTest = conflictables[referenceToTest]; // get team or adj
          if (typeof entityToTest !== 'undefined') {
            if (entityToTest.institution.id === institutionID) {
              entityToTest['conflicted'][hoverOrPanel][typeOfClash] = isConflicted;
            }
          }
        }
      }
    }
  }
}
</script>
