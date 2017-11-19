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
            if (!_.isUndefined(self.teamsById[clash.id])) {
              var clashName = self.teamsById[clash.id].short_name
              var clashIcon = 'message-circle'
            }
          } else if (clashesType === 'adjudicator') {
            if (!_.isUndefined(self.adjudicatorsById[clash.id])) {
              var clashName = self.adjShortName(self.adjudicatorsById[clash.id].name)
              var clashIcon = 'user'
            }
          } else if (clashesType === 'institution') {
            if (!_.isUndefined(self.institutionsById[clash.id])) {
              var clashName = self.institutionsById[clash.id].code
              var clashIcon = 'globe'
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
              var historyName = false // Saw someone not in current draw
            } else {
              var historyName = self.teamsById[history.id].short_name
            }
          } else if (historiesType === 'adjudicator') {
            if (_.isUndefined(self.adjudicatorsById[history.id])) {
              var historyName = false // Saw someone not in current draw
            } else {
              var historyName = self.adjShortName(self.adjudicatorsById[history.id].name)
            }
          }
          // Only push if the team/adj is present in the draw
          if (historyName) {
            var css = 'conflictable hover-histories-' + history.ago + '-ago'
            // Only show last 2 rounds for small screens
            if (history.ago > 2) { css += ' visible-lg-block' }
            formattedHistories.push({
              'title': historyName, 'ago': history.ago,
              'class': css, 'type': historiesType
            })
          }
        })
      })

      // Return if no histories
      if (formattedHistories.length === 0) {
        return formattedHistories
      }

      // Order by rounds;
      var histories = _.sortBy(formattedHistories, [function(h) {
        return h.ago
      }])

      // Add initial and subsequent round counter
      histories.splice(0, 0, {
        'title': '-' + histories[0].ago, 'icon': 'clock',
        'class': histories[0].ago > 2 ? ' visible-lg-block' : ' '
      })

      _.forEach(histories, function(history, i) {
        if (_.isUndefined(history['icon'])) {
          if (histories[i + 1].ago !== history.ago) {
            histories.splice(i + 1, 0, {
              'title': '-' + histories[i + 1].ago, 'icon': 'clock',
              'class': histories[i + 1].ago > 2 ? ' visible-lg-block' : ' '
            })
          }
        }
      })

      // Don't have too many items when they wont be shown anyway
      histories = histories.slice(0, 15)

      // Remove trailing round indicator if it's the last element
      if (!_.isUndefined(_.last(histories)['icon'])) {
        histories.pop()
      }
      return histories
    }
  }
}
</script>
