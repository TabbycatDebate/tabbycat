<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  props: {
    hasInstitutionalConflict: { default: false },
    hasPersonalConflict: { default: false },
    position: String,
    debateId: Number
  },
  methods: {
    setConflictHighlights: function() {
      var entity = this.getEntity()[0];
      this.$dispatch('set-conflicts', {
        personal_adjudicators: entity.conflicts.personal_adjudicators,
        personal_teams: entity.conflicts.personal_teams,
        institutional_institutions: entity.conflicts.institutional_institutions,
        institutional_adjudicators: entity.conflicts.institutional_adjudicators,
        uid: this._uid // To determine if hover target == conflict target
      })
    },
    unsetConflictHighlights: function() {
      this.$dispatch('unset-conflicts')
    },
  },
  computed: {
    conflictsHighlights: function() {
      // TODO set string based on dict

      // var conflicts = this.currentConflictHighlights;
      // if (!conflicts || conflicts === null || this._uid === conflicts.uid ) {
      //   // Don't add conflict highlights if there are none listed or if we are
      //   // currently hovering over an element
      //   return '';
      // } else {
      //   var entity = this.getEntity()[0];
      //   // Both
      //   if (conflicts.institutional_institutions && typeof conflicts.institutional_institutions !== 'undefined') {
      //     if (conflicts.institutional_institutions.indexOf(entity.institution.id) > -1) {
      //       return 'conflicts-display institutional-conflict'
      //     }
      //   }
      //   // Only for adjs
      //   if (this.getEntity()[1] === 'adj') {
      //     if (conflicts.personal_adjudicators && typeof conflicts.personal_adjudicators !== 'undefined') {
      //       if (conflicts.personal_adjudicators.indexOf(entity.id) > -1) {
      //         return 'conflicts-display personal-conflict'
      //       }
      //     }
      //     if (conflicts.institutional_adjudicators && typeof conflicts.institutional_adjudicators !== 'undefined') {
      //       if (conflicts.institutional_adjudicators.indexOf(entity.id) > -1) {
      //         return 'conflicts-display institutional-conflict'
      //       }
      //     }
      //   }

      //   // Only for Teams
      //   if (this.getEntity()[1] === 'team') {
      //     if (conflicts.personal_teams && typeof conflicts.personal_teams !== 'undefined') {
      //       if (conflicts.personal_teams.indexOf(entity.id) > -1) {
      //         return 'conflicts-display personal-conflict'
      //       }
      //     }
      //   }
      // }
    }
  }
}
</script>
