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
