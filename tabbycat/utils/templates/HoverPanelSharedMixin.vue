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
    makeInstitutionItem: function (subject) {
      let institutionDetails = []
      if (subject.institution) {
        let institution = this.institutions[this.subject.institution]
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
