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
        hover: { team: false, adjudicator: false, institution: false, seens: false },
        panel: { team: false, adjudicator: false, institution: false, seens: false },
      }
    }
  },
  created: function () {
    // Watch for issues clash events on the global event hub
    // These looklike 'set-conflicts-for-team-99
    // var eventCode = this.conflictableType + '-' + this.conflictable.id
    // this.$eventHub.$on('set-clashes-for-' + eventCode, this.setClashes)
    // this.$eventHub.$on('set-seens-for-' + eventCode, this.setSeens)
    // Institutions we need to do specially as they have a different ID
    // eventCode = 'institution-' + this.conflictable.institution.id
    // this.$eventHub.$on('set-clashes-for-' + eventCode, this.setClashes)
    // Turning off all hovers
    // this.$eventHub.$on('hide-all-hover-conflicts', this.unsetHoverConflicts)
  },
  computed: {
    // conflictableType: function() {
    //   if (!_.isUndefined(this.team)) { return 'team' }
    //   if (!_.isUndefined(this.adjudicator)) { return 'adjudicator' }
    // },
    // conflictable: function() {
    //   if (!_.isUndefined(this.team)) { return this.team }
    //   if (!_.isUndefined(this.adjudicator)) { return this.adjudicator }
    // },
    conflictsStatus: function() {
      var self = this
      var conflictsCSS = 'conflictable '
      _.forEach(_.keys(this.clashes), function(hoverOrPanel) {
        // Iterate over panel and hover states
        if (self.clashes[hoverOrPanel][self.conflictableType]) {
          conflictsCSS += hoverOrPanel + '-' + self.conflictableType
        }
        if (self.clashes[hoverOrPanel]['institution']) {
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
      // Issue conflict events; typically on beginning hover
      // this.$eventHub.$emit('show-conflicts-for', this.conflictable, this.conflictableType, 'hover', true)
    },
    hideConflicts: function() {
      // Issue conflict events; typically on ending hover
      // this.$eventHub.$emit('hide-all-hover-conflicts')
    },
    // setSeens: function(forHoverOrPanel, setState) {
    //   // Receive clash events indicating this item should be highlighted
    //   this.seens[forHoverOrPanel] = setState
    // },
    // setClashes: function(forHoverOrPanel, setState, clashType) {
    //   // Receive seen events indicating this item should be highlighted
    //   this.clashes[forHoverOrPanel][clashType] = setState
    // },
    // unsetHoverConflicts: function() {
    //   // When a unhovering over something it broadcasts to all objects
    //   // This is not very efficient but prevents state errors from drag/drops
    //   this.clashes.hover.team = false
    //   this.clashes.hover.adjudicator = false
    //   this.clashes.hover.institution = false
    //   this.seens.hover = false
    // }
  }
}
</script>
