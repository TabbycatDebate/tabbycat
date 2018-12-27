<script>
import { mapGetters } from 'vuex'
import ConflictableMixin from './ConflictableMixin.vue'

export default {
  mixins: [ConflictableMixin],
  computed: {
    hasClashConflict: function () {
      if (this.debateOrPanelId) {
        if (this.hasPanelClashConflict) {
          return true
        } else if (this.hasTeamClashConflict) {
          return true
        }
      }
      return false
    },
    hasInstitutionalConflict: function () {
      if (this.debateOrPanelId) {
        if (this.hasPanelInstitutionalConflict) {
          return true
        } else if (this.hasTeamInstitutionalConflict) {
          return true
        }
      }
      return false
    },
    hasHistoryConflict: function () {
      if (this.debateOrPanelId) {
        if (this.hasPanelHistoryConflict) {
          return this.hasPanelHistoryConflict
        } else if (this.hasTeamHistoryConflict) {
          return this.hasTeamHistoryConflict
        }
      }
      return false
    },
    hasPanelClashConflict: function () {
      // adj-adj personal clashes
      let debateAdjudicators = this.allDebatesOrPanels[this.debateOrPanelId].adjudicators
      let clashes = this.adjudicatorClashesForItem(this.adjudicator.id)
      if (clashes && 'adjudicator' in clashes) {
        for (let clash of clashes.adjudicator) {
          if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
            return true
          }
        }
      }
      return false
    },
    hasTeamClashConflict: function () {
      // adj-team personal clashes
      if (!('teams' in this.allDebatesOrPanels[this.debateOrPanelId])) {
        return false // For preformed panels
      }
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      let clashes = this.adjudicatorClashesForItem(this.adjudicator.id)
      if (clashes && 'team' in clashes) {
        for (let clash of clashes.team) {
          if (this.isTeamInDebateTeams(clash.id, debateTeams)) {
            return true
          }
        }
      }
      return false
    },
    hasPanelInstitutionalConflict: function () {
      // adj-adj institutional clashes
      let debateAdjudicators = this.allDebatesOrPanels[this.debateOrPanelId].adjudicators
      let clashes = this.adjudicatorClashesForItem(this.adjudicator.id)
      if (clashes && 'institution' in clashes) {
        for (let clash of clashes.institution) {
          if (this.isInstitutionInPanel(clash.id, debateAdjudicators, this.adjudicator.id)) {
            return true
          }
        }
      }
      return false
    },
    hasTeamInstitutionalConflict: function () {
      // adj-team institutional conflicts
      if (!('teams' in this.allDebatesOrPanels[this.debateOrPanelId])) {
        return false // For preformed panels
      }
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      let clashes = this.adjudicatorClashesForItem(this.adjudicator.id)
      if (clashes && 'institution' in clashes) {
        for (let clash of clashes.institution) {
          if (this.isInstitutionInDebateTeams(clash.id, debateTeams)) {
            return true
          }
        }
      }
      return false
    },
    hasPanelHistoryConflict: function () {
      // adj-adj history conflicts
      let debateAdjudicators = this.allDebatesOrPanels[this.debateOrPanelId].adjudicators
      let histories = this.adjudicatorHistoriesForItem(this.adjudicator.id)
      let smallestAgo = 99
      if (histories && 'adjudicator' in histories) {
        for (let history of histories.adjudicator) {
          if (this.isAdjudicatorInPanel(history.id, debateAdjudicators)) {
            if (history.ago < smallestAgo) {
              smallestAgo = history.ago // Want to ensure we show the most recent clash
            }
          }
        }
      }
      if (smallestAgo === 99) {
        return false
      } else {
        return smallestAgo
      }
    },
    hasTeamHistoryConflict: function () {
      // adj-team history conflicts
      if (!('teams' in this.allDebatesOrPanels[this.debateOrPanelId])) {
        return false // For preformed panels
      }
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      let histories = this.adjudicatorHistoriesForItem(this.adjudicator.id)
      if (histories && 'team' in histories) {
        for (let history of histories.team) {
          if (this.isTeamInDebateTeams(history.id, debateTeams)) {
            return history.ago
          }
        }
      }
      return false
    },
    ...mapGetters(['allDebatesOrPanels']),
  },
}
</script>
