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
      if (adjorteam.institution !== null) {
        var title = adjorteam.institution.name
        var css = ''
        if (adjorteam.region !== null && !_.isUndefined(adjorteam.region)) {
          title += ' (' + adjorteam.region.name + ')'
          css += 'region-display region-' + adjorteam.region.class
        }
        return [{ 'title': title, 'icon': 'globe', 'class': css }]
      } else {
        return [{ 'title': "No Institution", 'icon': 'globe', 'class': '' }]
      }
    },
  }
}
</script>
