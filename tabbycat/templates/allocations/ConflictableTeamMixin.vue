<script>
import { mapGetters } from 'vuex'
import ConflictableMixin from './ConflictableMixin.vue'

export default {
  mixins: [ConflictableMixin],
  computed: {
    hasClashConflict: function () {
      const debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      const clashes = this.teamClashesForItem(this.team.id)
      if (clashes && 'adjudicator' in clashes) {
        for (const clash of clashes.adjudicator) {
          if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
            return true
          }
        }
      }
      return false
    },
    hasInstitutionalConflict: function () {
      const debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      const clashes = this.teamClashesForItem(this.team.id)
      if (clashes && 'institution' in clashes) {
        for (const clash of clashes.institution) {
          if (this.isInstitutionInPanel(clash.id, debateAdjudicators, null)) {
            return true
          }
        }
      }
      return false
    },
    hasHistoryConflict: function () {
      const debateAdjudicators = this.allDebatesOrPanels[this.debateId].adjudicators
      const histories = this.teamHistoriesForItem(this.team.id)
      let smallestAgo = 99
      if (histories && 'adjudicator' in histories) {
        for (const clash of histories.adjudicator) {
          if (this.isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
            if (clash.ago < smallestAgo) {
              smallestAgo = clash.ago // Want to ensure we show the most recent clash
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
    ...mapGetters(['allDebatesOrPanels']),
  },
}
</script>
