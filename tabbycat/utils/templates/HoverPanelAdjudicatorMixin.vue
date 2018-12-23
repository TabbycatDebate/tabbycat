<script>

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
        if (this.subject.score > this.highlights.rank.options[rankCategory].fields.cutoff) {
          relevantCategory = this.highlights.rank.options[rankCategory]
          break
        }
      }
      let css = 'rank-display ' + relevantCategory.css // Derived from highlight
      let score = this.makeItem(`${this.subject.score} Feedback Score`, css, false)
      let rank = this.makeItem(`${relevantCategory.fields.name} Relevant Rank`, css, false)
      return [[score, rank]]
    },
    bottomleftadjudicator: function () {
      // Conflicts
      return []
    },
    bottomrightadjudicator: function () {
      // History
      return []
    },
  },
}
</script>
