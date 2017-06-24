<script>
// Subclass should set on the hoverable element:
// @mouseenter="showSlideOver( SUBJECT_DATA )
// @mouseleave="hideSlideOver( SUBJECT_DATA )
// Subclass should usually overrite formatForSlideOver() with their own data
// They pass up an array of 'rows' and an optional annotate method
// The annotate method allows the parent element to append data only it has
// such as conflict lookups
import _ from 'lodash'

export default {
  data: function () {
    return { slideOverSubject: null }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
  },
  methods: {
    setSlideover: function(object, annotateMethod, annotateObject) {
      var info = object
      if (annotateMethod) {
        var extraFeatures = this[annotateMethod](annotateObject)
        if (extraFeatures) {
          info['tiers'].push(extraFeatures)
        }
      }
      this.slideOverSubject = info
    },
    unsetSlideover: function() {
      this.slideOverSubject = null
    },
    addConflictsAnnotation: function(item) {
      return {
        'features': [
          this.getClashesForSlideOver(item),
          null,
          this.getHistoriesForSlideOver(item)
        ]
      }
    },
    getClashesForSlideOver: function(item) {
      var clashes = item.conflicts.clashes
      if (_.isUndefined(clashes) || !clashes) { return [] }
      var formattedClashes = []
      var self = this
      _.forEach(clashes, function(clashesList, clashesType) {
        _.forEach(clashesList, function(clash) {
          if (clashesType === 'team') {
            var clashName = self.teamsById[clash].short_name
            var clashIcon = 'glyphicon-comment'
          } else if (clashesType === 'adjudicator') {
            var clashName = self.adjudicatorsById[clash].name
            var clashIcon = 'glyphicon-user'
          } else if (clashesType === 'institution') {
            var clashName = self.institutionsById[clash].code
            var clashIcon = 'glyphicon-globe'
          }
          formattedClashes.push({'title': clashName, 'class': 'conflictable hover-' + clashesType, 'icon': clashIcon})
        })
      })
      return formattedClashes
    },
    getHistoriesForSlideOver: function(item) {
      var histories = item.conflicts.histories
      if (_.isUndefined(histories) || !histories) { return [] }
      var formattedHistories = []
      var self = this
      _.forEach(histories, function(historiesList, historiesType) {
        _.forEach(historiesList, function(history) {
          if (historiesType === 'team') {
            var historyName = self.teamsById[history.id].short_name
            var clashIcon = 'glyphicon-comment'
          } else if (historiesType === 'adjudicator') {
            var historyName = self.adjudicatorsById[history.id].name
            var clashIcon = 'glyphicon-user'
          }
          formattedHistories.push({
            'title': historyName + ' ' + history.ago + ' ago',
            'class': 'conflictable hover-history-' + history.ago + '-ago', 'icon': clashIcon})
        })
      })
      return formattedHistories
    }
  }
}
</script>
