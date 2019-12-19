<script>
// Must provide a computer properaty of highlightData pointing to adj/team/etc
// Then uses highlightsCSS within a :class property
import { mapState, mapGetters } from 'vuex'

export default {
  computed: {
    highlightsCSS: function () {
      return [this.activeClass, this.breakClass, this.genderClass, this.regionClass, this.categoryClass, this.rankClass].join(' ')
    },
    activeClass: function () {
      let currentKey = Object.keys(this.highlights).filter(key => this.highlights[key].active)
      if (currentKey.length > 0) {
        return currentKey + '-display'
      }
      return ''
    },
    breakClass: function () {
      if (
        typeof this.highlightData === 'object' && this.highlightData && 'break_categories' in this.highlightData &&
        this.highlights.break
      ) {
        var breakClasses = []
        let highlightCategories = Object.keys(this.highlights.break.options)
        for (let breakCategory of this.highlightData.break_categories) {
          let matchingCategory = highlightCategories.filter(
            bc => this.highlights.break.options[bc].pk === breakCategory)
          if (matchingCategory.length > 0) {
            breakClasses += ' ' + this.highlights.break.options[matchingCategory[0]].css
          }
        }
        return breakClasses
      }
      return ''
    },
    genderClass: function () {
      if (typeof this.highlightData === 'object' && this.highlightData !== null) {
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
      }
      return '' // Fallback
    },
    regionClass: function () {
      if (this.highlightData && 'institution' in this.highlightData) {
        const itemsInstitutionID = this.highlightData.institution
        if (itemsInstitutionID && 'region' in this.highlights) {
          if (itemsInstitutionID in this.allInstitutions) {
            const itemsInstitution = this.allInstitutions[itemsInstitutionID]
            const itemsRegion = this.highlights.region.options[itemsInstitution.region]
            if (itemsRegion) {
              return this.highlights.region.options[itemsInstitution.region].css
            }
          }
        }
      }
      return ''
    },
    categoryClass: function () {
      if (typeof this.highlightData === 'object' && this.highlightData && 'categories' in this.highlightData) {
        var catClasses = []
        let highlightCategories = Object.keys(this.highlights.category.options)
        for (let category of this.highlightData.categories) {
          let matchingCategory = highlightCategories.filter(
            vc => this.highlights.category.options[vc].pk === category.id)
          if (matchingCategory.length > 0) {
            catClasses += ' ' + this.highlights.category.options[matchingCategory[0]].css
          }
        }
        return catClasses
      }
      return ''
    },
    rankClass: function () {
      if (this.highlightData && 'score' in this.highlightData) {
        let rankCategories = Object.keys(this.highlights.rank.options)
        for (let rankCategory of rankCategories) {
          if (this.highlightData.score >= this.highlights.rank.options[rankCategory].fields.cutoff) {
            return this.highlights.rank.options[rankCategory].css
          }
        }
      }
      return ''
    },
    ...mapState(['highlights']),
    ...mapGetters(['allInstitutions']),
  },
  methods: { },
}
</script>
