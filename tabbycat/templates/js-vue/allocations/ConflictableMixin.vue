<script>
import ConflictUtilitiesMixin from './ConflictUtilitiesMixin.vue'
import _ from 'lodash'

export default {
  // An item that can be set into a conflicted state; either due to hover events
  // or due to in-panel conflicts. It does so by receiving a list of conflicts
  // from the global event hub and then checking if it matches with any of them.
  // It then sets an internal record or the conflicted state
  mixins: [ConflictUtilitiesMixin],
  data: function () {
    return {
      isConflicted: {
        hover: { team: false, adjudicator: false, institution: false, histories: false },
        panel: { team: false, adjudicator: false, institution: false, histories: false },
      },
      debugMode: true
    }
  },
  mounted: function () {
    // Watch for issues conflect events issued on the global event hub
    // These looklike 'set-conflicts-for-team-99 (histories, teams, true)
    var conflictCode = 'set-conflicts-for-' + this.conflictableType + '-' + this.conflictable.id
    this.$eventHub.$on(conflictCode, this.setConflicts)

    // Institutional conflicts are many to many; need to subscribe to all
    // var self = this
    // var institutionConflicts = this.conflictable.conflicts.clashes.institution
    // _.forEach(institutionConflicts, function(institutionConflict) {
    //   var conflictCode = 'institution' + '-' + institutionConflict
    //   self.$eventHub.$on('set-conflicts-for-' + conflictCode, self.setConflicts)
    // })

    // Turning off targetted panel conflicts
    var eventCode = 'unset-conflicts-for-' + this.conflictableType + '-' + this.conflictable.id
    this.$eventHub.$on(eventCode, this.unsetConflicts)
  },
  computed: {
    hasHistoryConflict: function() {
      // Used for the inline template element showing how long ago the seen was
      if (this.isConflicted.hover.histories) {
        return this.isConflicted.hover.histories
      } else if (this.isConflicted.panel.histories) {
        return this.isConflicted.panel.histories
      } else {
        return false
      }
    },
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
      if (this.debugMode) {
        console.debug('Conflictable showHoverConflicts() for', this.conflictableType,
          this.conflictable.id, this.isConflicted)
      }
      // Issue conflict events; typically on beginning hover
      var self = this
      this.forEachConflict(this.conflictable.conflicts,
        function(conflict, type, clashOrHistory) {
          self.sendConflict(conflict, type, 'hover', clashOrHistory)
        }
      )
    },
    hideHoverConflicts: function() {
      // Issue hide conflict events; typically on ending hover
      var self = this
      this.forEachConflict(this.conflictable.conflicts,
        function(conflict, type, clashOrHistory) {
          self.unsendConflict(conflict.id, type, 'hover')
        }
      )
    },
    setConflicts: function(hoverOrPanel, conflictType, state) {
      // Receive a conflict message from elsewhere and activate the conflict
      // if (conflictType === 'institution' && hoverOrPanel === 'hover') {
      //   if (originator === this.conflictable) {
      //     return // Institutional conflicts shouldn't self-conflict
      //   }
      // }
      if (this.debugMode) {
        console.debug('\t\tConflictable setConflicts() of type', conflictType, '-',
                      hoverOrPanel, 'for', this.conflictableType,
                      this.conflictable.id, 'as', state)
      }
      this.isConflicted[hoverOrPanel][conflictType] = state
    },
    unsetConflicts: function(hoverOrPanel) {
      // Receive a conflict message from elsewhere and deactivate the conflict
      // When a unhovering over something it broadcasts to all objects
      // This is not very efficient but prevents state errors from drag/drops
      if (this.debugMode) {
        console.debug('\t\tConflictable unsetConflicts() of all types', '-',
                      hoverOrPanel, this.conflictableType,
                      this.conflictable.id)
      }
      this.isConflicted[hoverOrPanel].team = false
      this.isConflicted[hoverOrPanel].adjudicator = false
      this.isConflicted[hoverOrPanel].institution = false
      this.isConflicted[hoverOrPanel].histories = false
    }
  }
}
</script>
