<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'

export default {
  mixins: [],
  computed: {
    venueCategoriesFeature: function () {
      const self = this
      const categories = _.map(this.venue.categories, vc => ({
        title: self.getCategoryName(vc),
        icon: 'tag',
      }))
      return categories
    },
  },
  methods: {
    getCategoryName: function (vc) {
      if (vc.description === '') {
        return vc.name
      }
      return `${vc.name} (${vc.description})`
    },
    formatForSlideOver: function () {
      return {
        tiers: [{
          features: [
            [{
              title: `${this.venue.name} (Priority of ${this.venue.priority})`,
              icon: 'map-pin',
            }],
            null,
            this.venueCategoriesFeature,
          ],
        }],
      }
    },
  },
}
</script>
