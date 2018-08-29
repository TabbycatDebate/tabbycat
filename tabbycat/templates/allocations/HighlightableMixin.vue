<script>
// Assumes highlightable objects; must provide a highlightableObject computed
// property that points to the base team/adj object
// They should then bind :class to include highlightsClasses
import _ from 'lodash'

export default {
  computed: {
    highlightsIdentity: function () {
      let classString = ''

      const region = this.highlightableObject.region
      if (!_.isUndefined(region) && region !== null) {
        classString += ` region-${region.class}`
      }
      const gender = this.getGender(this.highlightableObject)
      if (!_.isUndefined(gender) && gender !== null) {
        classString += gender
      }
      _.forEach(this.highlightableObject.break_categories, (category) => {
        classString += ` category-${category.class}`
      })
      return classString
    },
    highlightsStatus: function () {
      let classString = ''
      const highlights = this.highlightableObject.highlights

      if (highlights.region === true) {
        classString += ' region-display'
      }
      if (highlights.gender === true) {
        classString += ' gender-display'
      }
      if (highlights.category === true) {
        classString += ' category-display'
      }
      if (highlights.ranking === true) {
        classString += ' ranking-display'
      }
      return classString
    },
  },
  methods: {
    getGender: function (adjorteam) {
      if (!_.isUndefined(adjorteam.gender) && adjorteam.gender !== null) {
        return ` gender-${adjorteam.gender}`
      }
      if (!_.isUndefined(adjorteam.speakers)) {
        let classString = ''
        const men = _.filter(adjorteam.speakers, s => s.gender === 'M')
        const notmen = _.filter(adjorteam.speakers, s => s.gender === 'F' || s.gender === 'O')

        if (notmen.length > 0 || men.length > 0) {
          classString += ' has-gender '
        }
        classString += ` gender-men-${men.length} gender-notmen-${notmen.length}`
        return classString
      }
      return '' // Fallback
    },
  },
}
</script>
