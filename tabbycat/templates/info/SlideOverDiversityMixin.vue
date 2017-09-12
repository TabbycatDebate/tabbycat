<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  methods: {
    genderBrackets: function(gender) {
      if (gender) {
        return '(' + gender + ')'
      } else {
        return ''
      }
    },
    institutionDetailForSlideOver: function(adjorteam) {
      var title = adjorteam.institution.name
      var css = ''
      if (adjorteam.region !== null && !_.isUndefined(adjorteam.region)) {
        title += ' (' + adjorteam.region.name + ')'
        css += 'region-display region-' + adjorteam.region.class
      }
      return [{ 'title': title, 'icon': 'globe', 'class': css }]
    },
  }
}
</script>
