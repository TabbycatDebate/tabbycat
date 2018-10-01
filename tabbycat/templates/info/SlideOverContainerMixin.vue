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
    setSlideover: function (object, annotateMethod, annotateObject) {
      const info = object
      if (annotateMethod) {
        const extraFeatures = this[annotateMethod](annotateObject)
        if (extraFeatures) {
          info.tiers.push(extraFeatures)
        }
      }
      this.slideOverSubject = info
    },
    unsetSlideover: function () {
      this.slideOverSubject = null
    },
    addConflictsAnnotation: function (item) {
      return {
        features: [
          this.getClashesForSlideOver(item),
          null,
          this.getHistoriesForSlideOver(item),
        ],
      }
    },
    adjShortName (name) {
      const names = name.split(' ')
      if (names.length > 1) {
        const lastname = names[names.length - 1]
        const firstNames = name.split(` ${lastname}`).join('')
        return `${firstNames} ${lastname[0]}`
      }
      return names.join(' ')
    },
    getClashesForSlideOver: function (item) {
      if (!item.hasOwnProperty('conflicts') || !item.conflicts.hasOwnProperty('clashes')) {
        return []
      }

      const formattedClashes = []
      const self = this
      _.forEach(item.conflicts.clashes, (clashesList, clashesType) => {
        _.forEach(clashesList, (clash) => {
          let clashName = false
          let clashIcon = ''

          if (clashesType === 'team') {
            if (!_.isUndefined(self.teamsById[clash.id])) {
              clashName = self.teamsById[clash.id].short_name
              clashIcon = 'message-circle'
            }
          } else if (clashesType === 'adjudicator') {
            if (!_.isUndefined(self.adjudicatorsById[clash.id])) {
              clashName = self.adjShortName(self.adjudicatorsById[clash.id].name)
              clashIcon = 'user'
            }
          } else if (clashesType === 'institution') {
            if (!_.isUndefined(self.institutionsById[clash.id])) {
              clashName = self.institutionsById[clash.id].code
              clashIcon = 'globe'
            }
          }
          // Institution/Teams/Adjs may be clashed but not present in this draw
          if (clashName) {
            formattedClashes.push({
              title: clashName,
              class: `conflictable hover-${clashesType}`,
              icon: clashIcon,
            })
          }
        })
      })
      return formattedClashes
    },
    getHistoriesForSlideOver: function (item) {
      if (!item.hasOwnProperty('conflicts') || !item.conflicts.hasOwnProperty('histories')) {
        return []
      }

      const formattedHistories = []
      const self = this
      _.forEach(item.conflicts.histories, (historiesList, historiesType) => {
        _.forEach(historiesList, (history) => {
          let historyName = false

          if (historiesType === 'team') {
            if (_.isUndefined(self.teamsById[history.id])) {
              historyName = false // Saw someone not in current draw
            } else {
              historyName = self.teamsById[history.id].short_name
            }
          } else if (historiesType === 'adjudicator') {
            if (_.isUndefined(self.adjudicatorsById[history.id])) {
              historyName = false // Saw someone not in current draw
            } else {
              historyName = self.adjShortName(self.adjudicatorsById[history.id].name)
            }
          }
          // Only push if the team/adj is present in the draw
          if (historyName) {
            let css = `conflictable hover-histories-${history.ago}-ago`
            // Only show last 2 rounds for small screens
            if (history.ago > 2) { css += ' visible-lg-block' }
            formattedHistories.push({
              title: historyName,
              ago: history.ago,
              class: css,
              type: historiesType,
            })
          }
        })
      })

      // Return if no histories
      if (formattedHistories.length === 0) {
        return formattedHistories
      }

      // Order by rounds;
      let histories = _.sortBy(formattedHistories, [function (h) {
        return h.ago
      }])

      // Add initial and subsequent round counter
      histories.splice(0, 0, {
        title: `-${histories[0].ago}`,
        icon: 'clock',
        class: histories[0].ago > 2 ? ' visible-lg-block' : ' ',
      })

      _.forEach(histories, (history, i) => {
        if (_.isUndefined(history.icon)) {
          if (!_.isUndefined(histories[i + 1])) {
            if (histories[i + 1].ago !== history.ago) {
              histories.splice(i + 1, 0, {
                title: `-${histories[i + 1].ago}`,
                icon: 'clock',
                class: histories[i + 1].ago > 2 ? ' visible-lg-block' : ' ',
              })
            }
          }
        }
      })

      // Don't have too many items when they wont be shown anyway
      histories = histories.slice(0, 15)

      // Remove trailing round indicator if it's the last element
      if (!_.isUndefined(_.last(histories).icon)) {
        histories.pop()
      }
      return histories
    },
  },
}
</script>
