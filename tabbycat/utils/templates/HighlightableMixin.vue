<script>
// Must provide a computer properaty of highlightData pointing to adj/team/etc
// Then uses highlightsCSS within a :class property
import { mapState } from 'vuex'

export default {
  computed: {
    highlightsCSS: function () {
      return [this.activeClass, this.genderClass, this.regionClass].join(' ')
    },
    activeClass: function () {
      let currentKey = Object.keys(this.highlights).filter(key => this.highlights[key].active)
      if (currentKey.length > 0) {
        return currentKey + '-display'
      }
      return ''
    },
    genderClass: function () {
      if (this.highlightData && 'gender' in this.highlightData) {
        return ` gender-${this.highlightData.gender}` // Must be an adjudicator
      }
      if (this.highlightData && 'speakers' in this.highlightData) {
        let classString = ''
        const men = this.highlightData.speakers.filter(s => s.gender === 'M')
        const notmen = this.highlightData.speakers.filter(s => s.gender === 'F' || s.gender === 'O')
        classString += `gender-men-${men.length} gender-notmen-${notmen.length}`
        return classString
      }
      return '' // Fallback
    },
    regionClass: function () {
      const itemsInstitutionID = this.highlightData.institution
      console.log('itemsInstitutionID', itemsInstitutionID)
      if (itemsInstitutionID) {
        if (itemsInstitutionID in this.institutions) {
          const itemsInstitution = this.institutions[itemsInstitutionID]
          const itemsRegion = this.highlights.region.options[itemsInstitution.region]
          console.log('itemsInstitution', itemsInstitution)
          console.log('itemsRegion', itemsRegion)
          if (itemsRegion) {
            return this.highlights.region.options[itemsInstitution.region].css
          }
        }
      }
      return ''
    },
    ...mapState(['institutions', 'highlights']),
  },
  methods: { },
}
</script>
