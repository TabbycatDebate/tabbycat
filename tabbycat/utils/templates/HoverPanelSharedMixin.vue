<script>

export default {
  methods: {
    makeItem: function (title, css, icon) {
      return { 'title': title, 'css': css, 'icon': icon }
    },
    makePersonItem: function (participant) {
      return this.makeItem(
        participant.name + ` (${participant.gender ? participant.gender : '?'})`,
        `gender-display gender-${participant.gender}`,
        'user',
      )
    },
    makeClashItems: function (clashes) {
      let adjudicators = null
      if ('adjudicator' in clashes) {
        adjudicators = []
        for (let clash of clashes.adjudicator) {
          adjudicators.push(this.makeItem(this.allAdjudicators[clash.id].name, 'conflictable hover-adjudicator', ''))
        }
      }
      let institutions = null
      if ('institution' in clashes) {
        institutions = []
        for (let clash of clashes.institution) {
          institutions.push(this.makeItem(this.allInstitutions[clash.id].code, 'conflictable hover-institution', ''))
        }
      }
      let teams = null
      if ('team' in clashes) {
        teams = []
        for (let clash of clashes.team) {
          teams.push(this.makeItem(this.allTeams[clash.id].short_name, 'conflictable hover-team', ''))
        }
      }
      return [institutions, teams, adjudicators]
    },
    makeHistoryItems: function (histories) {
      let formattedHistories = {}
      if ('adjudicator' in histories) {
        for (let history of histories['adjudicator']) {
          if (!(history.ago in formattedHistories)) {
            let css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
            formattedHistories[history.ago] = [this.makeItem(`-${history.ago}R`, css, false)]
          }
          if (history.id in this.allAdjudicators) {
            let adjName = this.allAdjudicators[history.id].name.split(' ')[0]
            let css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
            formattedHistories[history.ago].push(this.makeItem(adjName, css, false))
          }
        }
      }
      if ('team' in histories && Object.keys(this.allTeams).length > 0) {
        for (let history of histories['team']) {
          if (!(history.ago in formattedHistories)) {
            let css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
            formattedHistories[history.ago] = [this.makeItem(`-${history.ago}R`, css, false)]
          }
          if (history.id in this.allTeams) {
            let teamName = this.allTeams[history.id].short_name
            let css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
            formattedHistories[history.ago].push(this.makeItem(teamName, css, false))
          }
        }
      }
      let historyItems = [] // Needs to be 2D array for display
      let roundKeys = Object.keys(formattedHistories).sort()
      for (let roundKey of roundKeys) {
        historyItems.push(formattedHistories[roundKey])
      }
      return historyItems
    },
    makeInstitutionItem: function (subject) {
      let institutionDetails = []
      if (subject.institution) {
        let institution = this.allInstitutions[this.subject.institution]
        if (institution.region) {
          let regionName = this.highlights.region.options[institution.region].fields.name
          let name = institution.code + ` (${!regionName ? 'No Region' : regionName})`
          let css = 'region-display ' + this.highlights.region.options[institution.region].css
          institutionDetails.push(this.makeItem(name, css, false))
        } else {
          let name = institution.code + ' (?)'
          let css = 'btn-outline-secondary'
          institutionDetails.push(this.makeItem(name, css, false))
        }
      }
      return institutionDetails
    },
  },
}
</script>
