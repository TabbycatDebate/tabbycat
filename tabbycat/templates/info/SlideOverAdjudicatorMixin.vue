<script>
// Mainly just handles formatting the object for the slideover
import SlideOverDiversityMixin from './SlideOverDiversityMixin.vue'
import _ from 'lodash'

export default {
  data: function () {
    return { annotationMethodName: 'addConflictsAnnotation' }
  },
  mixins: [SlideOverDiversityMixin],
  computed: {
    ratingsFeature: function() {
      var ratings = [{ 'title': this.adjudicator.score + ' Feedback Score',
                       'icon': 'wifi' }]
      // Percentile rankings only on Edit Adjudicators page
      if (!_.isUndefined(this.percentileRanking)) {
        ratings.push({
          'title': this.percentileRanking.grade + this.percentileRanking.text,
          'class': 'ranking-display ranking-' + this.percentileRanking.percentile
        })
      }
      return ratings
    },
    genderFeature: function() {
      var gender = [
        { 'title': this.adjudicator.name + ' (' + this.adjudicator.gender + ')',
          'class': 'gender-display gender-' + this.adjudicator.gender,
          'icon': 'user' }
      ]
      return gender
    },
    annotateDataForSlideOver: function() {
      return this.adjudicator
    }
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
