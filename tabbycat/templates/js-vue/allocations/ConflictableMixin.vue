<script>
import _ from 'lodash'

export default {
  // An item that can be set into a conflicted state; either due to hover events
  // or due to in-panel conflicts. It does so by receiving a list of conflicts
  // from the global event hub and then checking if it matches with any of them.
  // It then sets an internal record or the conflicted state

  data: function () {
    return {
      conflicts: {
        hover: { team: false, adjudicator: false, institution: false },
        panel: { team: false, adjudicator: false, institution: false },
      },
      seens: {
        hover: false,
        panel: false
      }
    }
  },
  created: function () {
    // Watch for issues clash events on the global event hub
    this.$eventHub.$on('set-conflicts-for', this.setConflicts)
  },
  computed: {
    conflictableType: function() {
      if (!_.isUndefined(this.team)) { return 'team' }
      if (!_.isUndefined(this.adjudicator)) { return 'adjudicator' }
    },
    conflictable: function() {
      if (!_.isUndefined(this.team)) { return this.team }
      if (!_.isUndefined(this.adjudicator)) { return this.adjudicator }
    },
    conflictsStatus: function() {
      var conflictsCSS = 'conflictable '
      var self = this
      _.forEach(_.keys(this.conflicts), function(hoverOrPanel) {
        // Iterate over panel and hover states
        if (self.conflicts[hoverOrPanel][self.conflictableType]) {
          conflictsCSS += hoverOrPanel + '-personal '
        }
        if (self.conflicts[hoverOrPanel]['institution']) {
          conflictsCSS += hoverOrPanel + '-institutional '
        }
      })
      _.forEach(_.keys(this.seens), function(hoverOrPanel) {
        // Iterate over panel and hover states
        if (self.seens[hoverOrPanel]) {
          conflictsCSS += hoverOrPanel + '-history-' + self.seens[hoverOrPanel] + '-ago'
        }
      })
      return conflictsCSS
    }
  },
  methods: {
    showConflicts: function() {
      // Issue conflict events; typically on hover on
      this.$eventHub.$emit('show-conflicts-for', this.conflictable, this.conflictableType, 'hover')
    },
    hideConflicts: function() {
      // Issue conflict events; typically on hover off
      this.$eventHub.$emit('hide-conflicts-for', this.conflictable, this.conflictableType, 'hover')
    },
    checkClashes: function(conflictingItem, conflicts, setState, hoverOrPanel) {
      // Check the given list of conflicts to see if this item's id is there
      if (conflictingItem === this.conflictable || _.isUndefined(conflicts)) {
        return
      }
      if (_.includes(conflicts[this.conflictableType], this.conflictable.id)) {
        this.conflicts[hoverOrPanel][this.conflictableType] = setState
      }
      if (_.includes(conflicts['institution'], this.conflictable.institution.id)) {
        this.conflicts[hoverOrPanel]['institution'] = setState
      }
    },
    checkHistories: function(histories, setState, hoverOrPanel) {
      // Check the given list of histories to see if this item's id is there
      if (!setState) {
        this.seens[hoverOrPanel] = false
      } else if (histories && !_.isUndefined(histories[this.conflictableType])) {
        var self = this
        var timesSeen = _.filter(histories[this.conflictableType], function(h) {
          return h.id === self.conflictable.id
        })
        if (timesSeen.length > 0) {
          var sortedByAgo = _.sortBy(timesSeen, [function(s) { return s.ago }])
          var lastSeen = sortedByAgo[0].ago
          this.seens[hoverOrPanel] = lastSeen
        }
      }
    },
    setConflicts: function(conflictingItem, conflicts, histories, setState, hoverOrPanel) {
      // if (this.conflictable.id === 77) {
      //   console.log('checking for justin', conflicts)
      // }
      this.checkClashes(conflictingItem, conflicts, setState, hoverOrPanel)
      this.checkHistories(histories, setState, hoverOrPanel)
    },
  }
}
</script>
