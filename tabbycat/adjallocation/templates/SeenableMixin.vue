<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      seen: false
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-seen-for', this.setConflicts)
  },
  computed: {
    seenableType: function() {
      if (!_.isUndefined(this.team)) { return 'team' }
      if (!_.isUndefined(this.adjudicator)) { return 'adjudicator' }
    },
    seenable: function() {
      if (!_.isUndefined(this.team)) { return this.team }
      if (!_.isUndefined(this.adjudicator)) { return this.adjudicator }
    },
    seensStatus: function() {
      var conflictsCSS = 'seenable '
      if (this.adjorteam.seen) {
        conflicts_class += ' seen' + this.roundsAgo + '-ago '
      }
      return conflictsCSS
    }
  },
  methods: {
    showSeen: function() {
      this.$eventHub.$emit('show-seens-for', this.conflictable, this.conflictableType)
    },
    hideSeen: function() {
      this.$eventHub.$emit('hide-seens-for', this.conflictable, this.conflictableType)
    },
    setConflicts: function(conflictingItem, conflicts, setState) {
      // Check the given list of conflicts to see if this item's id is there
      if (conflictingItem === this.conflictable) {
        return // Don't show self conflicts
      }
      if (_.includes(conflicts[this.conflictableType], this.conflictable.id)) {
        this.conflicted[this.conflictableType] = setState
      }
      if (_.includes(conflicts['institution'], this.conflictable.institution.id)) {
        this.conflicted['institution'] = setState
      }
    },
  }
}
</script>
