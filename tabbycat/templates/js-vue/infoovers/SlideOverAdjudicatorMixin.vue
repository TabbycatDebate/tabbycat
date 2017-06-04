<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  computed: {
    institutionDetailForSlideOver: function() {
      var adj = this.adjudicator
      if (adj.region === null || _.isUndefined(adj.region)) {
        return { 'title': adj.institution.code,
                 'icon': 'glyphicon-globe',
                 'class': '' }
      } else {
        return { 'title': adj.institution.name + ' (' + adj.region.name + ')',
                 'icon': 'glyphicon-globe',
                 'class': 'region-display region-' + adj.region.class }
      }
    },
  },
  methods: {
    formatForSlideOver: function(subject) {
      var adj = this.adjudicator
      return {
        'title': adj.name,
        'tiers': [{
          'features': [
            [{ 'title': adj.name + ' (' + adj.gender +  ')',
                      'class': 'gender-display gender-' + adj.gender,
                      'icon': 'glyphicon-user' }],
            [this.institutionDetailForSlideOver],
            [{ 'title': adj.score + ' Feedback',
                      'class': '',
                      'icon': 'glyphicon-signal' },
                    { 'title': 'A+ Percentile (X%)',
                      'class': '',
                      'icon': 'glyphicon-ok' }],
          ]},
        ]
      }
    }
  }
}
</script>
