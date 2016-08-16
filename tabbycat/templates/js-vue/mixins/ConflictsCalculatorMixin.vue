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
        // Set history value and rounds_ago to be the lowest possible match
        if (typeof entity !== 'undefined') {
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
      this.findMatchingConflicts(conflicts.adjudicators, origin,
        this.conflictableAdjudicators, conflictState, 'personal', conflictValue, false)
      this.findMatchingConflicts(conflicts.teams, origin,
        this.conflictableTeams, conflictState, 'personal', conflictValue, false)
      this.findMatchingConflicts(conflicts.institutions, origin,
        this.conflictableAdjudicators, conflictState, 'institutional', conflictValue, true)
      this.findMatchingConflicts(conflicts.institutions, origin,
        this.conflictableTeams, conflictState, 'institutional', conflictValue, true)
    },
    unsetAll: function(conflictState, conflictables) {
      // Sometimes, such as on panel calcs can't toggle of in a pinpoint manner
      // So we do so in bulk for all conflictables and properties
      for (var reference in conflictables) {
        if (conflictables.hasOwnProperty(reference)) {
          var entity = conflictables[reference]
          entity.conflicted[conflictState]['history'] = false;
          entity.conflicted[conflictState]['institutional'] = false;
          entity.conflicted[conflictState]['personal'] = false;
        }
      }
    },
    findMatchingConflicts: function(conflicts, origin, conflictables, hoverOrPanel, typeOfClash, isConflicted, isInstitutional) {
      // Loop through all conflicts; dispatch to Individual/Institutional
      if (typeof conflicts === 'undefined' || conflicts === null) {
        return
      }
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
    findMatchingInstitutionalConflict: function(conflictables, origin, conflictedInstitutionID, hoverOrPanel, typeOfClash, isConflicted) {
      // Loop through all possible conflictables and check for institutional ID matches
      for (var key in conflictables) {
        if (conflictables.hasOwnProperty(key)) {
          var entityToTest = conflictables[key];
          if (entityToTest.type === 'team' && origin.type === 'team') {
            // Dont count team-team institution conflicts as such
          } else if (entityToTest === origin) {
            // Dont check self
          } else if (typeof entityToTest === 'undefined') {
            // Catchall
          } else {
            // Rather than checking the entity's institution we loop through all
            // of their institutional conflicts (a super set) to ensure symmetry
            var targetsInstitutionalConflicts = entityToTest.conflicts.institutions
            for (var i = 0; i < targetsInstitutionalConflicts.length; i++) {
              // Check for institution ID match with each originating conflict
              if (targetsInstitutionalConflicts[i] === conflictedInstitutionID) {
                entityToTest['conflicted'][hoverOrPanel][typeOfClash] = isConflicted;
              }
            }
          }
        }
      }
    }
  }
}
</script>
