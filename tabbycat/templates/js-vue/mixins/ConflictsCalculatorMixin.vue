<script>
// Controller for calculating and setting conflicts/history highlights
// Inheriting classes should set conflictableTeams/conflictableAdjudicators
// as a computed property to return subsets of teams/adjs to check for

export default {
  methods: {
    toggleHistories: function(conflictValue, conflictState, origin, histories) {
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
        // console.log('    checking conflicted history for ', entity)
        // Set history value and rounds_ago to be the lowest possible match
        if (typeof entity !== 'undefined') {
          // console.log('    setting conflicted history for ', entity.name)
          entity.conflicted[conflictState]['history'] = conflictValue;
          if (history.ago < entity.conflicted[conflictState]['history_ago']) {
            entity.conflicted[conflictState]['history_ago'] = history.ago;
          }
        }
      });
    },
    toggleConflicts: function(conflictValue, conflictState, origin, conflicts) {
      if (typeof conflicts === 'undefined' || conflicts === null) {
        return
      }
      var searchableAdjudicators = this.conflictableAdjudicators;
      var searchableTeams = this.conflictableTeams;

      this.findMatchingConflicts(conflicts.adjudicators, origin,
        searchableAdjudicators, conflictState, 'personal', conflictValue, false)
      this.findMatchingConflicts(conflicts.teams, origin,
        searchableTeams, conflictState, 'personal', conflictValue, false)

      this.findMatchingConflicts(conflicts.institutions, origin,
        searchableAdjudicators, conflictState, 'institutional', conflictValue, true)
      this.findMatchingConflicts(conflicts.institutions, origin,
        searchableTeams, conflictState, 'institutional', conflictValue, true)
    },
    findMatchingConflicts: function(conflicts, origin, conflictables, hoverOrPanel, typeOfClash, isConflicted, isInstitutional) {
      // Loop through all conflicts; dispatch to Individual/Institutional
      if (typeof conflicts === 'undefined' || conflicts === null) {
        return
      }
      // if (typeOfClash === 'panel') {
      //   console.log('    findMatchingConflicts', conflicts, conflictables, hoverOrPanel);
      // }
      var _this = this;
      conflicts.forEach(function(conflictedID) {
        if (isInstitutional === false) {
          _this.findIndividualConflict(conflictables, origin,
            conflictedID, hoverOrPanel, typeOfClash, isConflicted)
        } else if (isInstitutional === true) {
          _this.findMatchingInstitutionalConflict(conflictables, origin,
            conflictedID, hoverOrPanel, typeOfClash, isConflicted)
        }
      })
    },
    findIndividualConflict: function(conflictables, origin, conflictedID, hoverOrPanel, typeOfClash, isConflicted) {
      // For each known conflict, check if ID is in the list of conflictables
      var conflictMatch = conflictables[conflictedID];
      if (typeof conflictMatch !== 'undefined') {
        conflictMatch['conflicted'][hoverOrPanel][typeOfClash] = isConflicted
      }
    },
    findMatchingInstitutionalConflict: function(conflictables, origin, institutionID, hoverOrPanel, typeOfClash, isConflicted) {
      // Loop through all possible conflictables and check for institutional ID matches
      for (var referenceToTest in conflictables) {
        if (conflictables.hasOwnProperty(referenceToTest)) {
          var entityToTest = conflictables[referenceToTest]; // get team or adj
          if (typeof entityToTest !== 'undefined' && entityToTest !== origin) { // don't highlight originator as institutional clash
            if (entityToTest.institution.id === institutionID) { // check for institution match
              entityToTest['conflicted'][hoverOrPanel][typeOfClash] = isConflicted;
            }
          }
        }
      }
    }
  }
}
</script>
