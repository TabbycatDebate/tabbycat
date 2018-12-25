<script>
import { mapGetters } from 'vuex'
import ConflictableMixin from './ConflictableMixin.vue'

export default {
  mixins: [ConflictableMixin],
  computed: {
    hasClashConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      for (let clash of this.teamClashesForItem(this.team.id).adjudicator) {
        if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          return true
        }
      }
      return false
    },
    hasInstitutionalConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      for (let clash of this.teamClashesForItem(this.team.id).institution) {
        if (this.isInstitutionInPanel(clash.id, debateAdjudicators, null)) {
          return true
        }
      }
      return false
    },
    hasHistoryConflict: function () {
      let debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      let histories = this.teamHistoriesForItem(this.team.id)
      if (histories && 'adjudicator' in histories) {
        for (let clash of this.teamHistoriesForItem(this.team.id).adjudicator) {
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
