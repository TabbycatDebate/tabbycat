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
      let points = this.subject.points ? this.subject.points : 0 // Points can be null
      let pointsDetails = [this.makeItem(`On ${points} Points`, 'btn-outline-secondary', false)]
      for (let bc of this.subject.break_categories) {
        let category = this.highlights.break.options[bc]
        if (category) {
          let breakCSS = 'break-display ' + category.css
          let status = '?'
          if (this.subject.points >= category.fields.safe) {
            status = 'SAFE'
          } else if (this.subject.points <= category.fields.dead) {
            status = 'DEAD'
          } else if (this.subject.points > category.fields.dead && this.subject.points < category.fields.safe) {
            status = 'LIVE'
          }
          let item = this.makeItem(`${status} for ${category.fields.name}`, breakCSS, false)
          pointsDetails.push(item)
        }
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
