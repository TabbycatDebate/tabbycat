<script>
import { mapGetters } from 'vuex'

export default {
  methods: {
    isInstitutionInPanel: function (idToFind, debateAdjudicators, debateAdjudicatorToExclude) {
      let found = false
      Object.keys(debateAdjudicators).forEach(adjudicatorPosition => {
        for (const adjudicatorId of debateAdjudicators[adjudicatorPosition]) {
          if (adjudicatorId === debateAdjudicatorToExclude) {
            continue
          }
          // Need to find the adjudicator's own institutional conflicts to compare
          let adjsInstitutionalConflicts = this.adjudicatorClashesForItem(adjudicatorId)
          if (adjsInstitutionalConflicts && 'institution' in adjsInstitutionalConflicts) {
            for (const institutionalConflict of adjsInstitutionalConflicts.institution) {
              if (institutionalConflict.id === idToFind) {
                found = true
                break
              }
            }
          }
        }
      })
      return found
    },
    isInstitutionInDebateTeams: function (idToFind, debateTeams) {
      // Search for the institutional conflict amongst the conflicts of the teams present
      let found = false
      Object.keys(debateTeams).forEach(debateTeamPosition => {
        let team = debateTeams[debateTeamPosition]
        if (team !== null) { // Handle when sides editing may be in progress
          let teamsInstitutionalConflicts = this.teamClashesForItem(team.id).institution
          for (const institutionalConflict of teamsInstitutionalConflicts) {
            if (institutionalConflict.id === idToFind) {
              found = true
              break
            }
          }
        }
      })
      return found
    },
    isAdjudicatorInPanel: function (idToFind, debateAdjudicators) {
      let found = false
      Object.keys(debateAdjudicators).forEach(adjudicatorPosition => {
        for (const adjudicatorId of debateAdjudicators[adjudicatorPosition]) {
          if (adjudicatorId === idToFind) {
            found = true
            break
          }
        }
      })
      return found
    },
    isTeamInDebateTeams: function (idToFind, debateTeams) {
      let found = false
      Object.keys(debateTeams).forEach(teamPosition => {
        if (debateTeams[teamPosition].id === idToFind) {
          found = true
        }
      })
      return found
    },
  },
  computed: {
    conflictsCSS: function () {
      if (this.hasClashConflict) {
        return 'conflictable panel-adjudicator'
      } else if (this.hasInstitutionalConflict) {
        return 'conflictable panel-institution'
      } else if (this.hasHistoryConflict) {
        return `conflictable panel-histories-${this.hasHistoryConflict}-ago`
      }
      return ''
    },
    ...mapGetters(['adjudicatorClashesForItem', 'teamClashesForItem',
      'adjudicatorHistoriesForItem', 'teamHistoriesForItem']),
  },
}
</script>
