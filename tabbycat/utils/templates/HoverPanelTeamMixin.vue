<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    topleftteam: function () {
      let teamDetails = []
      teamDetails.push(this.makeItem(this.subject.short_name, 'btn-outline-secondary', false))
      if (this.extra.codeNames !== 'off') {
        teamDetails.push(this.makeItem(this.subject.code_name, 'btn-outline-secondary', false))
      }
      let speakerDetails = []
      for (let speaker of this.subject.speakers) {
        speakerDetails.push(this.makePersonItem(speaker))
      }
      let institutionDetails = this.makeInstitutionItem(this.subject)
      return [teamDetails, speakerDetails, institutionDetails]
    },
    toprightteam: function () {
      let points = this.subject.points ? this.subject.points : 0 // Points can be null
      let pointsDetails = [this.makeItem(`On ${points} Points`, 'btn-outline-secondary', false)]
      if (this.subject.break_categories.length === 0) {
        let item = this.makeItem(`No Break Categories Set`, 'btn-outline-secondary', false)
        pointsDetails.push(item)
      } else {
        for (let bc of this.subject.break_categories) {
          let category = this.highlights.break.options[bc]
          if (category) {
            let breakCSS = 'break-display ' + category.css
            let status = '?'
            let info = ''
            if (this.subject.points >= category.fields.safe) {
              status = 'SAFE'
              info = `(>${category.fields.safe - 1})`
            } else if (this.subject.points <= category.fields.dead) {
              status = 'DEAD'
              info = `(<${category.fields.dead + 1})`
            } else if (this.subject.points > category.fields.dead && this.subject.points < category.fields.safe) {
              status = 'LIVE'
              info = `(>${category.fields.dead})`
            }
            let item = this.makeItem(`${status} for ${category.fields.name} ${info}`, breakCSS, false)
            pointsDetails.push(item)
          }
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
