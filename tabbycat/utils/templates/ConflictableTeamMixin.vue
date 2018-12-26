<script>
import { mapGetters } from 'vuex'
import ConflictableMixin from './ConflictableMixin.vue'

export default {
  mixins: [ConflictableMixin],
  computed: {
    hasClashConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      let clashes = this.teamClashesForItem(this.team.id)
      if (clashes && 'adjudicator' in clashes) {
        for (let clash of clashes.adjudicator) {
          if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
            return true
          }
        }
      }
      return false
    },
    hasInstitutionalConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      let clashes = this.teamClashesForItem(this.team.id)
      if (clashes && 'institution' in clashes) {
        for (let clash of clashes.institution) {
          if (this.isInstitutionInPanel(clash.id, debateAdjudicators, null)) {
            return true
          }
        }
      }
      return false
    },
    hasHistoryConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      let histories = this.teamHistoriesForItem(this.team.id)
      if (histories && 'adjudicator' in histories) {
        for (let clash of histories.adjudicator) {
          if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
            return clash.ago
          }
        }
      }
      return false
    },
    ...mapGetters(['allDebatesOrPanels']),
  },
}
</script>
