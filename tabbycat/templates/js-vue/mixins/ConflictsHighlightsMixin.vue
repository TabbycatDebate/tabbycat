<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  methods: {
    setConflictHighlights: function() {
      var entity = this.getEntity()[0];
      this.$dispatch('set-conflicts', {
        adjudicators: entity.conflicts.adjadj,
        institutions: entity.conflicts.adjinstitution,
        teams: entity.conflicts.adjteam,
        uid: this._uid // To determine if hover target == conflict target
      })
    },
    unsetConflictHighlights: function() {
      this.$dispatch('unset-conflicts')
    },
  },
  computed: {
    conflictsHighlights: function() {
      var conflicts = this.currentConflictHighlights;
      if (!conflicts || conflicts === null || this._uid === conflicts.uid ) {
        // Don't add conflict highlights if there are none listed or if we are
        // currently hovering over an element
        return '';
      } else {
        var entity = this.getEntity()[0];
        // Institutional
        if (conflicts.institutions && typeof conflicts.institutions !== 'undefined') {
          var conflictedInsts = conflicts.institutions;
          if (conflictedInsts.indexOf(entity.institution.id) > -1) {
            return 'conflicts-display institutional-conflict'
          }
        }
        if (this.getEntity()[1] === 'adj') {
          // Personal (adj-adj)
          if (conflicts.adjudicators && typeof conflicts.adjudicators !== 'undefined') {
            var conflictedAdjs = conflicts.adjudicators;
            if (conflictedAdjs.indexOf(entity.id) > -1) {
              return 'conflicts-display personal-conflict'
            }
          }
        }
        if (this.getEntity()[1] === 'team') {
          // Personal (adj-adj)
          if (conflicts.teams && typeof conflicts.teams !== 'undefined') {
            var conflictedTeams = conflicts.teams;
            if (conflictedTeams.indexOf(entity.id) > -1) {
              return 'conflicts-display personal-conflict'
            }
          }
        }

      }
    }
  }
}
</script>
