<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  computed: {
    institutionDetailForSlideOver: function() {
      if (this.team.region === null || _.isUndefined(this.team.region)) {
        return { 'title': this.team.institution.name,
                 'icon': 'glyphicon-globe',
                 'class': '' }
      } else {
        return { 'title': this.team.institution.code + ' (' + this.team.region.name + ')',
                 'icon': 'glyphicon-globe',
                 'class': 'region-display region-' + this.team.region.class }
      }
    },
  },
  methods: {
    formatForSlideOver: function(subject) {
      return {
        'title': this.team.long_name,
        'tiers': [{
          'features': [
            _.map(this.team.speakers, function(s) {
              return { 'title': s.name + ' (' + s.gender +  ')',
                       'class': 'gender-display gender-' + s.gender,
                       'icon': 'glyphicon-user' }}),
            [this.institutionDetailForSlideOver],
            _.map(this.team.break_categories, function(bc) {
              return { 'title': bc.name + ' Break',
                       'class': 'category-display category-' + bc.class,
                       'icon': 'glyphicon-ok' }}),
          ]},
        ]
      }
    }
  }
}
</script>
