<script>
// Must provide a computer properaty of highlightData pointing to adj/team/etc
// Then uses highlightsCSS within a :class property
import { mapState, mapGetters } from 'vuex'

export default {
  computed: {
    highlightsCSS: function () {
      return [
        this.activeClass,
        this.breakClass, // Teams
        this.genderClass, // Teams or Adjs
        this.regionClass, // Teams or Adjs
        this.rankClass, // Adjs
        this.priorityClass, // Venues
        this.categoryClass, // Venues
      ].join(' ')
    },
    activeClass: function () {
      const currentKey = Object.keys(this.highlights).filter(key => this.highlights[key].active)
      if (currentKey.length > 0) {
        return currentKey + '-display'
      }
      return ''
    },
    breakClass: function () {
      return this.getCSSForOverlapping('break_categories', 'break')
    },
    categoryClass: function () {
      return this.getCSSForOverlapping('categories', 'category')
    },
    genderClass: function () {
      if (this.highlightData && typeof this.highlightData === 'object') {
        if ('gender' in this.highlightData) {
          return ` gender-${this.highlightData.gender}` // Must be an adjudicator
        }
      }
      if (this.highlightData && typeof this.highlightData === 'object') {
        if ('speakers' in this.highlightData) {
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
      if (this.highlightData && typeof this.highlightData === 'object') {
        if ('institution' in this.highlightData) {
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
      }
      return ''
    },
    rankClass: function () {
      return this.getCSSForOrder('score', 'rank')
    },
    priorityClass: function () {
      return this.getCSSForOrder('priority', 'priority')
    },
    ...mapState(['highlights']),
    ...mapGetters(['allInstitutions']),
  },
  methods: {
    getCSSForOverlapping: function (highlightKey, highlightType) {
      if (typeof this.highlightData === 'object' && this.highlightData && highlightKey in this.highlightData) {
        var classes = []
        const highlightCategories = Object.keys(this.highlights[highlightType].options)
        for (const category of this.highlightData[highlightKey]) {
          let matchingCategory = []
          if (typeof category === 'object') {
            matchingCategory = highlightCategories.filter(
              bc => this.highlights[highlightType].options[bc].pk === category.id)
          } else {
            matchingCategory = highlightCategories.filter(
              bc => this.highlights[highlightType].options[bc].pk === category)
          }
          if (matchingCategory.length > 0) {
            classes += ' ' + this.highlights[highlightType].options[matchingCategory[0]].css
          }
        }
        return classes
      }
      return ''
    },
    getCSSForOrder: function (highlightKey, highlightType) {
      if (this.highlightData && typeof this.highlightData === 'object') {
        if (highlightKey in this.highlightData) {
          const orderedCategories = Object.keys(this.highlights[highlightType].options)
          for (const category of orderedCategories) {
            if (this.highlightData[highlightKey] >= this.highlights[highlightType].options[category].fields.cutoff) {
              return this.highlights[highlightType].options[category].css
            }
          }
        }
      }
      return ''
    },
  },
}
</script>
