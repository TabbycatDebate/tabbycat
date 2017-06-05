<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  mixins: [],
  computed: {
    venueCategoriesFeature: function(vc) {
      var self = this
      var categories = _.map(this.venue.categories, function(vc) {
        return {
          'title': self.getCategoryName(vc),
          'icon': 'glyphicon-tags'
        }
      })
      return categories
    },
  },
  methods: {
    getCategoryName: function(vc) {
      if (vc.description === "") {
        return vc.name
      } else {
        return vc.name + ' (' + vc.description + ')'
      }
    },
    formatForSlideOver: function(subject) {
      return {
        'title': this.venue.name + ' (Priority of ' + this.venue.priority + ')',
        'tiers': [{
          'features': [
            this.venueCategoriesFeature,
            // this.institutionDetailForSlideOver(this.team),
            // this.categoriesFeature()
          ]
        }]
      }
    }
  }
}
</script>
