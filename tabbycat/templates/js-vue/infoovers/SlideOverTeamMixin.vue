<script>
// Mainly just handles formatting the object for the slideover
import SlideOverDiversityMixin from '../infoovers/SlideOverDiversityMixin.vue'
import _ from 'lodash'

export default {
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
      var teamInfo = { 'title': this.team.long_name }
      var speakersInfo = _.map(this.team.speakers, function(s) {
        return {
          'title': s.name + self.genderNameForSlideOver(s),
          'class': 'gender-display gender-' + s.gender,
          'icon': 'glyphicon-user'
        }
      })
      return _.concat(teamInfo, speakersInfo)
    }
  },
  methods: {
    titleForBC: function(bc, wins) {
      return bc.will_break.toUpperCase() + ' for ' + bc.name + ' Break'
    },
    iconForBC: function(bc) {
      if (bc.will_break === 'dead') { return 'glyphicon-remove' } else
      if (bc.will_break === 'safe') { return 'glyphicon-ok' } else
      if (bc.will_break === 'live') { return 'glyphicon-star' }
    },
    formatForSlideOver: function(subject) {
      return {
        'tiers': [{
          'features': [
            this.teamInfoFeature,
            null,
            this.breakCategoriesFeature,
          ]
        }]
      }
    }
  }
}
</script>
