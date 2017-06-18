<script>
// Assumes highlightable objects; must provide a highlightableObject computed
// property that points to the base team/adj object
// They should then bind :class to include highlightsClasses
import _ from 'lodash'

export default {
  computed: {
    highlightsIdentity: function() {
      var classString = ""
      var region = this.highlightableObject.region
      if (!_.isUndefined(region) && region !== null) {
        classString += " region-" + region.class
      }
      var gender = this.getGender(this.highlightableObject)
      if (!_.isUndefined(gender) && gender !== null) {
        classString += gender
      }
      _.forEach(this.highlightableObject.break_categories, function(category) {
        classString += " category-" + category.class
      });
      return classString
    },
    highlightsStatus: function() {
      var highlights = this.highlightableObject.highlights
      var classString = ""
      if (highlights.region === true) {
        classString += " region-display"
      }
      if (highlights.gender === true) {
        classString += " gender-display"
      }
      if (highlights.category === true) {
        classString += " category-display"
      }
      if (highlights.ranking === true) {
        classString += " ranking-display"
      }
      return classString
    },
  },
  methods: {
    getGender: function(adjorteam) {
      if (!_.isUndefined(adjorteam.gender) && adjorteam.gender !== null) {
        return " gender-" + adjorteam.gender
      }
      if (!_.isUndefined(adjorteam.speakers)) {
        var class_string = ""
        var men = _.filter(adjorteam.speakers, function(s) {
          return s.gender === "M"
        })
        var notmen = _.filter(adjorteam.speakers, function(s) {
          return s.gender === "F" || s.gender === "O"
        })
        if (notmen.length > 0 || men.length > 0) {
          class_string += ' has-gender '
        }
        class_string += ' gender-men-' + men.length + ' gender-notmen-' + notmen.length

        return class_string
      }
      return "" // Fallback
    }
  }
}
</script>
