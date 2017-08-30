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
    breakCategoriesFeature: function() {
      var self = this
      var winInfo = [{ 'title': self.team.wins + ' wins' }]
      var bcInfo = _.map(this.team.break_categories, function(bc) {
        return {
          'title': self.titleForBC(bc),
          'class': 'category-display category-' + bc.class,
          'icon': self.iconForBC(bc)
        }
      })
      return winInfo.concat(bcInfo)
    },
    teamInfoFeature: function() {
      var self = this
      var teamInfo = { 'title': this.team.short_name }
      var speakersInfo = _.map(this.team.speakers, function(s) {
        return {
          'title': s.name + ' (' + s.gender + ')',
          'class': 'gender-display gender-' + s.gender,
          'icon': 'user'
        }
      })
      return _.concat(teamInfo, speakersInfo)
    },
    annotateDataForSlideOver: function() {
      return this.team
    }
  },
  methods: {
    titleForBC: function(bc, wins) {
      if (!_.isUndefined(bc.will_break)) {
        return bc.will_break.toUpperCase() + ' for ' + bc.name
      }
    },
    iconForBC: function(bc) {
      if (bc.will_break === 'dead') { return 'x' } else
      if (bc.will_break === 'safe') { return 'check' } else
      if (bc.will_break === 'live') { return 'star' }
    },
    formatForSlideOver: function(subject) {
      return {
        'tiers': [{
          'features': [
            this.teamInfoFeature,
            this.institutionDetailForSlideOver(this.team),
            this.breakCategoriesFeature,
          ]
        }]
      }
    },
  }
}
</script>
