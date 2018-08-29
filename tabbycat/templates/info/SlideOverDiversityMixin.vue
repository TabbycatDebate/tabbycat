<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  methods: {
    genderBrackets: function (gender) {
      if (gender) {
        return `(${gender})`
      }
      return ''
    },
    institutionDetailForSlideOver: function (adjorteam) {
      if (adjorteam.institution !== null) {
        let title = adjorteam.institution.name
        let css = ''
        if (adjorteam.region !== null && !_.isUndefined(adjorteam.region)) {
          title += ` (${adjorteam.region.name})`
          css += `region-display region-${adjorteam.region.class}`
        }
        return [{ title: title, icon: 'globe', class: css }]
      }
      return [{ title: 'No Institution', icon: 'globe', class: '' }]
    },
  },
}
</script>
