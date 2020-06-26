<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    topleftadjudicator: function () {
      const adjDetails = [this.makePersonItem(this.subject)]
      const institutionDetails = this.makeInstitutionItem(this.subject)
      return [adjDetails, institutionDetails]
    },
    toprightadjudicator: function () {
      const rankCategories = Object.keys(this.highlights.rank.options)
      let relevantCategory = null
      for (const rankCategory of rankCategories) {
        if (this.subject.score >= this.highlights.rank.options[rankCategory].fields.cutoff) {
          relevantCategory = this.highlights.rank.options[rankCategory]
          break
        }
      }
      const css = 'rank-display ' + relevantCategory.css // Derived from highlight
      const roundedScore = Number.parseFloat(this.subject.score).toFixed(1) // Round to 1DP
      const score = this.makeItem(`${roundedScore} Feedback Score`, css, false)
      const rank = this.makeItem(`${relevantCategory.fields.name} Relevant Rank`, css, false)
      return [[score, rank]]
    },
    bottomleftadjudicator: function () {
      // Conflicts
      const clashes = this.adjudicatorClashesForItem(this.subject.id)
      if (clashes) {
        return this.makeClashItems(clashes)
      }
      return null
    },
    bottomrightadjudicator: function () {
      // History
      const histories = this.adjudicatorHistoriesForItem(this.subject.id)
      if (histories) {
        return this.makeHistoryItems(histories)
      }
      return null
    },
    ...mapGetters(['adjudicatorClashesForItem', 'adjudicatorHistoriesForItem']),
  },
}
</script>
