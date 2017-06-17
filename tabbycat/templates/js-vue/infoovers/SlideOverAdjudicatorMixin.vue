<script>
// Mainly just handles formatting the object for the slideover
import SlideOverDiversityMixin from '../infoovers/SlideOverDiversityMixin.vue'
import _ from 'lodash'

export default {
  mixins: [SlideOverDiversityMixin],
  computed: {
    ratingsFeature: function() {
      var ratings = [
        { 'title': this.adjudicator.score + ' Feedback', 'icon': 'glyphicon-signal' },
        { 'title': this.percentileRanking.grade + this.percentileRanking.text }
      ]
      return ratings
    },
    genderFeature: function() {
      var gender = [
        { 'title': this.adjudicator.name + this.genderNameForSlideOver(this.adjudicator),
          'class': 'gender-display gender-' + this.adjudicator.gender,
          'icon': 'glyphicon-user' }
      ]
      return gender
    },
  },
  methods: {
    formatForSlideOver: function(subject) {
      return {
        'tiers': [{
          'features': [
            this.genderFeature,
            this.institutionDetailForSlideOver(this.adjudicator),
            this.ratingsFeature
          ]
        }]
      }
    },
  }
}
</script>
