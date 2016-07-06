<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide an entity that has an ID property to match with conflicts

export default {
  props: {
    debateId: Number,
  },
  computed: {
    historiesHighlights: function() {
      if (this.adjorteam.hasHistoryConflict) {
        return ' histories-display seen-' + this.adjorteam.historyRoundsAgo + '-ago'
      } else {
        return ''
      }
    }
  },
  methods: {
    setHistoriesHighlights: function() {
      this.$dispatch('set-histories', this.adjorteam.histories)
    },
    unsetHistoriesHighlights: function() {
      this.$dispatch('unset-histories')
    },
  }
}
</script>
