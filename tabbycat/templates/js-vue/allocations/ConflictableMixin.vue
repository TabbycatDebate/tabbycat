<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      conflicted: { team: false, adjudicator: false, institution: false },
      seen: false
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
        conflictsCSS += 'conflict-personal '
      }
      if (this.conflicted['institution']) {
        conflictsCSS += 'conflict-institutional '
      }
      if (this.seen) {
        conflictsCSS += 'conflict-history-' + this.seen + '-ago'
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
    checkClashes: function(conflictingItem, conflicts, setState) {
      // Check the given list of conflicts to see if this item's id is there
      if (conflictingItem !== this.conflictable) {
        if (_.includes(conflicts[this.conflictableType], this.conflictable.id)) {
          this.conflicted[this.conflictableType] = setState
        }
        if (_.includes(conflicts['institution'], this.conflictable.institution.id)) {
          this.conflicted['institution'] = setState
        }
      }
    },
    checkHistories: function(histories, setState) {
      // Histories
      if (!setState) {
        this.seen = false
      } else if (histories && !_.isUndefined(histories[this.conflictableType])) {
        var self = this
        var timesSeen = _.filter(histories[this.conflictableType], function(h) {
          return h.id === self.conflictable.id
        })
        if (timesSeen.length > 0) {
          var sortedByAgo = _.sortBy(timesSeen, [function(s) { return s.ago }])
          var lastSeen = sortedByAgo[0].ago
          this.seen = lastSeen
        }
      }
    },
    setConflicts: function(conflictingItem, conflicts, histories, setState) {
      this.checkClashes(conflictingItem, conflicts, setState)
      this.checkHistories(histories, setState)
    },
  }
}
</script>
