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
      for (let clash of this.adjudicatorClashesForItem(this.adjudicator.id).adjudicator) {
        if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          return true
        }
      }
      return false
    },
    hasTeamClashConflict: function () {
      // adj-team personal clashes
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      for (let clash of this.adjudicatorClashesForItem(this.adjudicator.id).team) {
        if (this.isTeamInDebateTeams(clash.id, debateTeams)) {
          return true
        }
      }
      return false
    },
    hasPanelInstitutionalConflict: function () {
      // adj-adj institutional clashes
      let debateAdjudicators = this.allDebatesOrPanels[this.debateOrPanelId].adjudicators
      for (let clash of this.adjudicatorClashesForItem(this.adjudicator.id).institution) {
        if (this.isInstitutionInPanel(clash.id, debateAdjudicators, this.adjudicator.id)) {
          return true
        }
      }
      return false
    },
    hasTeamInstitutionalConflict: function () {
      // adj-team institutional conflicts
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      for (let clash of this.adjudicatorClashesForItem(this.adjudicator.id).institution) {
        if (this.isInstitutionInDebateTeams(clash.id, debateTeams)) {
          return true
        }
      }
      return false
    },
    hasPanelHistoryConflict: function () {
      // adj-adj history conflicts
      let debateAdjudicators = this.allDebatesOrPanels[this.debateOrPanelId].adjudicators
      for (let clash of this.adjudicatorHistoriesForItem(this.adjudicator.id).adjudicator) {
        if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          return clash.ago
        }
      }
      return false
    },
    hasTeamHistoryConflict: function () {
      // adj-team history conflicts
      let debateTeams = this.allDebatesOrPanels[this.debateOrPanelId].teams
      for (let clash of this.adjudicatorHistoriesForItem(this.adjudicator.id).team) {
        if (this.isTeamInDebateTeams(clash.id, debateTeams)) {
          return clash.ago
        }
      }
      return false
    },
    ...mapGetters(['allDebatesOrPanels']),
  },
}
</script>
