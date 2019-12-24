<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    topleftadjudicator: function () {
      let adjDetails = [this.makePersonItem(this.subject)]
      let institutionDetails = this.makeInstitutionItem(this.subject)
      return [adjDetails, institutionDetails]
    },
    toprightadjudicator: function () {
      let rankCategories = Object.keys(this.highlights.rank.options)
      let relevantCategory = null
      for (let rankCategory of rankCategories) {
        if (this.subject.score >= this.highlights.rank.options[rankCategory].fields.cutoff) {
          relevantCategory = this.highlights.rank.options[rankCategory]
          break
        }
      }
      let css = 'rank-display ' + relevantCategory.css // Derived from highlight
      let roundedScore = Number.parseFloat(this.subject.score).toFixed(1) // Round to 1DP
      let score = this.makeItem(`${roundedScore} Feedback Score`, css, false)
      let rank = this.makeItem(`${relevantCategory.fields.name} Relevant Rank`, css, false)
      return [[score, rank]]
    },
    bottomleftadjudicator: function () {
      // Conflicts
      let clashes = this.adjudicatorClashesForItem(this.subject.id)
      if (clashes) {
        return this.makeClashItems(clashes)
      }
    },
    bottomrightadjudicator: function () {
      // History
      let histories = this.adjudicatorHistoriesForItem(this.subject.id)
      if (histories) {
        return this.makeHistoryItems(histories)
      }
    },
    ...mapGetters(['adjudicatorClashesForItem', 'adjudicatorHistoriesForItem']),
  },
}
</script>
