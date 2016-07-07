<script>
// Provides methods for determining which CSS classes should be active when
// an adj or team's conflicted state has been set for a particular type
// Also provides method for dispatching a dictionary of conflicts from an
// adj or team that can be used as an action upon hoverning/clicking etc

export default {
  computed: {
    // Methods for showing/hiding CSS classes based on conflict states
    conflictsHighlights: function () {
      var adjorteam = this.adjorteam;
      if (adjorteam.conflicted.hover.personal || adjorteam.conflicted.panel.personal ) {
        return ' conflicts-display personal-conflict'
      } else if (adjorteam.conflicted.hover.institutional || adjorteam.conflicted.panel.institutional) {
        return ' conflicts-display institutional-conflict'
      }
    },
    historiesHighlights: function() {
      var adjorteam = this.adjorteam;
      if (adjorteam.conflicted.hover.history) {
        return ' histories-display seen-' + adjorteam.conflicted.hover.history_ago + '-ago'
      } else if (adjorteam.conflicted.panel.history) {
        return ' histories-display seen-' + adjorteam.conflicted.panel.history_ago + '-ago'
      } else {
        return ''
      }
    },
  },
  methods: {
    setConflictHighlights: function(dispatch) {
      this.$dispatch(dispatch, this.adjorteam.conflicts, this.adjorteam.histories)
    },
    unsetConflictHighlights: function(dispatch) {
      this.$dispatch(dispatch, this.adjorteam.conflicts, this.adjorteam.histories);
    },
  }
}
</script>
