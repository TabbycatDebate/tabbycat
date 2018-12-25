<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    topleftteam: function () {
      let teamDetails = [this.makeItem(this.subject.short_name, 'btn-outline-secondary', false)]
      for (let speaker of this.subject.speakers) {
        teamDetails.push(this.makePersonItem(speaker))
      }
      let institutionDetails = this.makeInstitutionItem(this.subject)
      return [teamDetails, institutionDetails]
    },
    toprightteam: function () {
      let pointsDetails = [this.makeItem(`On ${this.subject.points} Points`, 'btn-outline-secondary', false)]
      for (let bc of this.subject.break_categories) {
        let category = this.highlights.break.options[bc]
        let regionCSS = 'region-display ' + this.highlights.region.options[bc].css
        let item = this.makeItem(`STATUS for ${category.fields.name}`, regionCSS, false)
        pointsDetails.push(item)
      }
      return [pointsDetails]
    },
    bottomleftteam: function () {
      // Conflicts
      let clashes = this.teamClashesForItem(this.subject.id)
      if (clashes) {
        return this.makeClashItems(clashes)
      }
    },
    bottomrightteam: function () {
      // History
      let histories = this.teamHistoriesForItem(this.subject.id)
      if (histories) {
        return this.makeHistoryItems(histories)
      }
    },
    ...mapGetters(['teamClashesForItem', 'teamHistoriesForItem']),
  },
}
</script>
