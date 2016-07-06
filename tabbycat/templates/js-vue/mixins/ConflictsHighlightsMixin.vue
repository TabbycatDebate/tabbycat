<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  computed: {
    conflictsHighlights: function () {
      var class_string = " "
      var adjorteam = this.adjorteam;
      if (adjorteam.hasPersonalConflict) {
        return ' conflicts-display personal-conflict'
      } else if (adjorteam.hasInstitutionalConflict) {
        return ' conflicts-display institutional-conflict'
      }
    }
  },
  methods: {
    setConflictHighlights: function() {
      var adjorteam = this.adjorteam;
      this.$dispatch('set-conflicts', {
        personal_adjudicators: adjorteam.conflicts.personal_adjudicators,
        personal_teams: adjorteam.conflicts.personal_teams,
        institutional_conflicts: adjorteam.conflicts.institutional_conflicts,
        currentOrigin: adjorteam // To determine if hover target == conflict target
      })
    },
    unsetConflictHighlights: function() {
      this.$dispatch('unset-conflicts');
    },
  }
}
</script>
