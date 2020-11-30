<script>

export default {
  methods: {
    makeItem: function (title, css, icon) {
      return { title: title, css: css, icon: icon }
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
        for (const clash of clashes.adjudicator) {
          adjudicators.push(this.makeItem(this.allAdjudicators[clash.id].name, 'conflictable hover-adjudicator', ''))
        }
      }
      let institutions = null
      if ('institution' in clashes) {
        institutions = []
        for (const clash of clashes.institution) {
          institutions.push(this.makeItem(this.allInstitutions[clash.id].code, 'conflictable hover-institution', ''))
        }
      }
      let teams = null
      if ('team' in clashes && this.allTeams) {
        teams = []
        for (const clash of clashes.team) {
          if (clash.id in this.allTeams) {
            teams.push(this.makeItem(this.allTeams[clash.id].short_name, 'conflictable hover-team', ''))
          }
        }
      }
      return [institutions, teams, adjudicators]
    },
    makeHistoryItems: function (histories) {
      const formattedHistories = {}
      if ('adjudicator' in histories) {
        for (const history of histories.adjudicator) {
          if (!(history.ago in formattedHistories)) {
            const css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
            formattedHistories[history.ago] = [this.makeItem(`-${history.ago}R`, css, false)]
          }
          if (history.id in this.allAdjudicators) {
            const adjName = this.allAdjudicators[history.id].name.split(' ')[0]
            const css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
            formattedHistories[history.ago].push(this.makeItem(adjName, css, false))
          }
        }
      }
      if ('team' in histories && Object.keys(this.allTeams).length > 0) {
        for (const history of histories.team) {
          if (!(history.ago in formattedHistories)) {
            const css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
            formattedHistories[history.ago] = [this.makeItem(`-${history.ago}R`, css, false)]
          }
          if (history.id in this.allTeams) {
            const teamName = this.allTeams[history.id].short_name
            const css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
            formattedHistories[history.ago].push(this.makeItem(teamName, css, false))
          }
        }
      }
      const historyItems = [] // Needs to be 2D array for display
      const roundKeys = Object.keys(formattedHistories).sort()
      for (const roundKey of roundKeys) {
        historyItems.push(formattedHistories[roundKey])
      }
      return historyItems
    },
    makeInstitutionItem: function (subject) {
      const institutionDetails = []
      if (subject.institution) {
        const institution = this.allInstitutions[this.subject.institution]
        if (institution.region && this.highlights.region) {
          const regionName = this.highlights.region.options[institution.region].fields.name
          const name = institution.code + ` (${!regionName ? 'No Region' : regionName})`
          const css = 'region-display ' + this.highlights.region.options[institution.region].css
          institutionDetails.push(this.makeItem(name, css, false))
        } else {
          const name = institution.code
          const css = 'btn-outline-secondary'
          institutionDetails.push(this.makeItem(name, css, false))
        }
      }
      return institutionDetails
    },
  },
}
</script>
