<script>
import _ from 'lodash'

export default {
  // An item that can be set into a conflicted state; either due to hover events
  // or due to in-panel conflicts. It does so by receiving a list of conflicts
  // from the global event hub and then checking if it matches with any of them.
  // It then sets an internal record or the conflicted state
  data: function () {
    return {
      isConflicted: {
        hover: { team: false, adjudicator: false, institution: false, histories: false },
        panel: { team: false, adjudicator: false, institution: false, histories: false },
      }
    }
  },
  created: function () {
    // Watch for issues clash events on the global event hub
    // These looklike 'set-conflicts-for-team-99 (histories, teams, true)
    var conflictCode = this.conflictableType + '-' + this.conflictable.id
    this.$eventHub.$on('set-conflicts-for-' + conflictCode, this.setConflicts)
    var conflictCode = 'institution' + '-' + this.conflictable.institution.id
    this.$eventHub.$on('set-conflicts-for-' + conflictCode, this.setConflicts)
    // Turning off all hovers
    this.$eventHub.$on('unset-conflicts', this.unsetConflicts)
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
      var self = this
      var conflictsCSS = 'conflictable'
      _.forEach(this.isConflicted, function(conflictsCategories, hoverOrPanel) {
        _.forEach(conflictsCategories, function(conflictStatus, conflictType) {
          // Iterate over panel and hover states
          if (conflictStatus !== false) {
            conflictsCSS += ' ' + hoverOrPanel + '-' + conflictType
            if (conflictType === 'histories') {
              conflictsCSS += '-' + conflictStatus + '-ago'
            }
          }
        })
      })
      return conflictsCSS
    }
  },
  methods: {
    showHoverConflicts: function() {
      // Issue conflict events; typically on beginning hover
      var self = this
      _.forEach(this.conflictable.conflicts, function(conflictsCategories, clashOrHistory) {
        _.forEach(conflictsCategories, function(conflictsList, conflictType) {
          _.forEach(conflictsList, function(conflict) {
            if (clashOrHistory === 'clashes') {
              var eventCode = 'set-conflicts-for-' + conflictType + '-' + conflict
              self.$eventHub.$emit(eventCode, 'hover', conflictType, true)
            } else if (clashOrHistory === 'histories') {
              var eventCode = 'set-conflicts-for-' + conflictType + '-' + conflict.id
              self.$eventHub.$emit(eventCode, 'hover', 'histories', conflict.ago)
            }
          })
        })
      })
    },
    hideHoverConflicts: function() {
      // Issue hide conflict events; typically on ending hover
      this.$eventHub.$emit('unset-conflicts', 'hover')
    },
    setConflicts: function(hoverOrPanel, conflictType, state) {
      // console.log('setConflicts: ', hoverOrPanel, conflictType, state)
      this.isConflicted[hoverOrPanel][conflictType] = state
    },
    unsetConflicts: function(hoverOrPanel) {
      // When a unhovering over something it broadcasts to all objects
      // This is not very efficient but prevents state errors from drag/drops
      this.isConflicted[hoverOrPanel].team = false
      this.isConflicted[hoverOrPanel].adjudicator = false
      this.isConflicted[hoverOrPanel].institution = false
      this.isConflicted[hoverOrPanel].histories = false
    }
  }
}
</script>
