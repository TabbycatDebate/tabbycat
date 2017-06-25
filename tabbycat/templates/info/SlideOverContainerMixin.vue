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
    adjShortName(name) {
      var names = name.split(" ")
      if (names.length > 1) {
        var lastname = names[names.length - 1]
        var firstNames = name.split(" " + lastname).join("")
        return firstNames + " " + lastname[0]
      }
      return names.join(" ")
    },
    getClashesForSlideOver: function(item) {
      var clashes = item.conflicts.clashes
      if (_.isUndefined(clashes) || !clashes) { return [] }
      var formattedClashes = []
      var self = this
      _.forEach(clashes, function(clashesList, clashesType) {
        _.forEach(clashesList, function(clash) {
          var clashName = false
          if (clashesType === 'team') {
            if (!_.isUndefined(self.teamsById[clash])) {
              var clashName = self.teamsById[clash].short_name
              var clashIcon = 'glyphicon-comment'
            }
          } else if (clashesType === 'adjudicator') {
            if (!_.isUndefined(self.adjudicatorsById[clash])) {
              var clashName = self.adjShortName(self.adjudicatorsById[clash].name)
              var clashIcon = 'glyphicon-user'
            }
          } else if (clashesType === 'institution') {
            if (!_.isUndefined(self.institutionsById[clash])) {
              var clashName = self.institutionsById[clash].code
              var clashIcon = 'glyphicon-globe'
            }
          }
          // Institution/Teams/Adjs may be clashed but not present in this draw
          if (clashName) {
            formattedClashes.push({
              'title': clashName, 'class': 'conflictable hover-' + clashesType,
              'icon': clashIcon
            })
          }
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
            if (_.isUndefined(self.teamsById[history.id])) {
              var historyName = 'Unknown' // Saw someone not in current draw
            } else {
              var historyName = self.teamsById[history.id].short_name
            }
          } else if (historiesType === 'adjudicator') {
            if (_.isUndefined(self.adjudicatorsById[history.id])) {
              var historyName = 'Unknown' // Saw someone not in current draw
            } else {
              var historyName = self.adjShortName(self.adjudicatorsById[history.id].name)
            }
          }
          var css = 'conflictable hover-histories-' + history.ago + '-ago'
          // Only show last 2 rounds for small screens
          if (history.ago > 2) { css += ' visible-lg-block' }
          formattedHistories.push({'title': historyName, 'ago': history.ago, 'class': css})
        })
      })
      // Order by rounds;
      formattedHistories = _.sortBy(formattedHistories, [function(h) { return h.ago }])
      // Add round counter
      var countedRounds = []
      _.forEach(formattedHistories, function(history, index) {
        if (!_.includes(countedRounds, history.ago)) {
          formattedHistories.splice(index, 0, {
            'title': '-' + history.ago, 'icon': 'glyphicon-time',
            'class': history.ago > 2 ? ' visible-lg-block' : ' '
          })
          countedRounds.push(history.ago)
        }
      })
      formattedHistories = formattedHistories.slice(0,15)
      return formattedHistories
    }
  }
}
</script>
