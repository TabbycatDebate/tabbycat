<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    topleftteam: function () {
      const teamDetails = []
      if (this.extra.codeNames !== 'everywhere') {
        teamDetails.push(this.makeItem(this.subject.short_name, 'btn-outline-secondary', false))
      }
      if (this.extra.codeNames !== 'off') {
        let codeName = this.subject.code_name
        if (codeName === '') {
          codeName = this.gettext('No code name set')
        }
        teamDetails.push(this.makeItem(codeName, 'btn-outline-secondary', false))
      }
      const speakerDetails = []
      if (typeof this.subject.speakers !== 'undefined') {
        for (const speaker of this.subject.speakers) {
          speakerDetails.push(this.makePersonItem(speaker))
        }
      }
      const institutionDetails = this.makeInstitutionItem(this.subject)
      return [teamDetails, speakerDetails, institutionDetails]
    },
    toprightteam: function () {
      const points = this.subject.points ? this.subject.points : 0 // Points can be null
      const pointsDetails = [this.makeItem(`On ${points} Points`, 'btn-outline-secondary', false)]
      if (this.subject.break_categories.length === 0) {
        const item = this.makeItem('No Break Categories Set', 'btn-outline-secondary', false)
        pointsDetails.push(item)
      } else if (this.highlights.break) {
        for (const bc of this.subject.break_categories) {
          const category = this.highlights.break.options[bc]
          if (category) {
            const breakCSS = 'break-display ' + category.css
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
            const item = this.makeItem(`${status} for ${category.fields.name} ${info}`, breakCSS, false)
            pointsDetails.push(item)
          }
        }
      }
      return [pointsDetails]
    },
    bottomleftteam: function () {
      // Conflicts
      const clashes = this.teamClashesForItem(this.subject.id)
      if (clashes) {
        return this.makeClashItems(clashes)
      }
      return null
    },
    bottomrightteam: function () {
      // History
      const histories = this.teamHistoriesForItem(this.subject.id)
      if (histories) {
        return this.makeHistoryItems(histories)
      }
      return null
    },
    ...mapGetters(['teamClashesForItem', 'teamHistoriesForItem']),
  },
}
</script>
