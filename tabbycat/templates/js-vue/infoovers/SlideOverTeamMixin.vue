<script>
// Mainly just handles formatting the object for the slideover
import SlideOverDiversityMixin from '../infoovers/SlideOverDiversityMixin.vue'
import _ from 'lodash'

export default {
  mixins: [SlideOverDiversityMixin],
  computed: {
    breakCategoriesFeature: function() {
      var categories = _.map(this.team.break_categories, function(bc) {
        return {
          'title': bc.name + ' Break',
          'class': 'category-display category-' + bc.class,
          'icon': 'glyphicon-ok'
        }
      })
      return categories
    },
    speakersFeature: function() {
      var self = this
      var speakers = _.map(this.team.speakers, function(s) {
        return {
          'title': s.name + self.genderNameForSlideOver(s),
          'class': 'gender-display gender-' + s.gender,
          'icon': 'glyphicon-user'
        }
      })
      return speakers
    }
  },
  methods: {
    formatForSlideOver: function(subject) {
      return {
        'title': this.team.long_name,
        'tiers': [{
          'features': [
            this.speakersFeature,
            this.institutionDetailForSlideOver(this.team),
            this.breakCategoriesFeature
          ]
        }]
      }
    }
  }
}
</script>
