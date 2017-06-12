<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      conflicted: { team: false, adjudicator: false, institution: false }
    }
  },
  created: function () {
    // Watch for events on the global event hub
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
      if (this.conflicted[this.conflictableType]) {
        conflictsCSS += 'conflict-hover-personal-conflict '
      }
      if (this.conflicted['institution']) {
        conflictsCSS += 'conflict-hover-institutional-conflict '
      }
      return conflictsCSS
    }
  },
  methods: {
    showConflicts: function() {
      this.$eventHub.$emit('show-conflicts-for', this.conflictable, this.conflictableType)
    },
    hideConflicts: function() {
      this.$eventHub.$emit('hide-conflicts-for', this.conflictable, this.conflictableType)
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