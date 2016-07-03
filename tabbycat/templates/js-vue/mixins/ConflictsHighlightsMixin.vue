<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  props: {
    debateId: Number,
  },
  methods: {
    setConflictHighlights: function() {
      var entity = this.entity;
      this.$dispatch('set-conflicts', {
        personal_adjudicators: entity.conflicts.personal_adjudicators,
        personal_teams: entity.conflicts.personal_teams,
        institutional_institutions: entity.conflicts.institutional_institutions,
        institutional_adjudicators: entity.conflicts.institutional_adjudicators,
        uid: this._uid // To determine if hover target == conflict target
      })
    },
    unsetConflictHighlights: function() {
      this.$dispatch('unset-conflicts');
    },
  }
}
</script>
