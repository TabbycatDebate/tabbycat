<script>
// Provides methods for determining which CSS classes should be active when
// an adj or team's conflicted state has been set for a particular type
// Also provides method for dispatching a dictionary of conflicts from an
// adj or team that can be used as an action upon hoverning/clicking etc

export default {
  computed: {
    // Methods for showing/hiding CSS classes based on conflict states
    conflictsHighlights: function () {
      var conflicts_class = 'conflictable '
      if (this.adjorteam.conflicted.hover.personal) {
        conflicts_class += ' conflict-hover-personal-conflict '
      } else if (this.adjorteam.conflicted.hover.institutional) {
        conflicts_class += ' conflict-hover-institutional-conflict '
      } else if (this.adjorteam.conflicted.hover.history) {
        conflicts_class += ' conflict-hover-' + this.historyHighlightText + '-ago '
      }
      if (this.adjorteam.conflicted.panel.personal ) {
        conflicts_class += ' conflict-panel-personal-conflict '
      } else if (this.adjorteam.conflicted.panel.institutional) {
        conflicts_class += ' conflict-panel-institutional-conflict '
      } else if (this.adjorteam.conflicted.panel.history) {
        conflicts_class += ' conflict-panel-' + this.historyHighlightText + '-ago '
      }
      return conflicts_class
    },
    historyHighlightText: function() {
      if (this.adjorteam.conflicted.hover.history === true) {
        return this.adjorteam.conflicted.hover.history_ago
      } else if (this.adjorteam.conflicted.panel.history === true) {
        return this.adjorteam.conflicted.panel.history_ago
      } else {
        return false
      }
    }
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
