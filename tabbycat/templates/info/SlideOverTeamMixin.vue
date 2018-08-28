<script>
// Mainly just handles formatting the object for the slideover
import _ from 'lodash'
import SlideOverDiversityMixin from './SlideOverDiversityMixin.vue'

export default {
  data: function () {
    return { annotationMethodName: 'addConflictsAnnotation' }
  },
  mixins: [SlideOverDiversityMixin],
  computed: {
    breakCategoriesFeature: function () {
      const self = this
      let resultsInfo
      if (this.roundInfo.teamsInDebate === 'bp') {
        resultsInfo = [{ title: `On ${self.team.points} points` }]
      } else {
        resultsInfo = [{ title: `On ${self.team.wins} wins` }]
      }
      const bcInfo = _.map(this.team.break_categories, bc => ({
        title: self.titleForBC(bc),
        class: self.classForBC(bc),
        icon: self.iconForBC(bc),
      }))
      return resultsInfo.concat(bcInfo)
    },
    teamInfoFeature: function () {
      const self = this
      const teamInfo = { title: this.team.short_name }
      const speakersInfo = _.map(this.team.speakers, s => ({
        title: `${s.name} ${self.genderBrackets(s.gender)}`,
        class: `gender-display gender-${s.gender}`,
        icon: 'user',
      }))
      return _.concat(teamInfo, speakersInfo)
    },
    annotateDataForSlideOver: function () {
      return this.team
    },
  },
  methods: {
    titleForBC: function (bc) {
      if (!_.isUndefined(bc.will_break)) {
        if (bc.will_break !== null) {
          return `${bc.will_break.toUpperCase()} for ${bc.name} Break`
        }
        return `${bc.name} Break`
      }
      return null
    },
    classForBC: function (bc) {
      if (bc.will_break === 'dead' || bc.will_break === 'safe') {
        return `category-display category-${bc.class}-disabled`
      }
      return `category-display category-${bc.class}`
    },
    iconForBC: function (bc) {
      if (bc.will_break === 'dead') { return 'x' } else
      if (bc.will_break === 'safe') { return 'check' } else
      if (bc.will_break === 'live') { return 'star' }
      return ''
    },
    formatForSlideOver: function () {
      return {
        tiers: [{
          features: [
            this.teamInfoFeature,
            this.institutionDetailForSlideOver(this.team),
            this.breakCategoriesFeature,
          ],
        }],
      }
    },
  },
}
</script>
