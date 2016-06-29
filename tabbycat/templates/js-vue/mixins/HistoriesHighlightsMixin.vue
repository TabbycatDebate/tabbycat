<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide a getEntity() that has an ID property to match with conflicts

export default {
  methods: {
    setHistoriesHighlights: function() {
      var entity = this.getEntity()[0];
      this.$dispatch('set-histories', entity.histories)
    },
    unsetHistoriesHighlights: function() {
      this.$dispatch('unset-histories')
    },
  },
  computed: {
    historiesHighlights: function() {
      var histories = this.currentHistoriesHighlights;
      if (!histories || histories === null) {
        return '';
      } else {
        var entity = this.getEntity()[0];
        var match = '';

        // Search for first matching adj element
        if (this.getEntity()[1] === 'adj') {
          for (var i=0, iLen=histories.length; i<iLen; i++) {
            if (histories[i].adj == entity.id) {
              match = 'histories-display seen-' + histories[i].ago + '-ago';
              break;
            }
          }
        }
        // Search for first matching team element
        if (this.getEntity()[1] === 'team') {
          for (var i=0, iLen=histories.length; i<iLen; i++) {
            if (histories[i].team == entity.id) {
              match = 'histories-display seen-' + histories[i].ago + '-ago';
              break;
            }
          }
        }
        return match;

      }
    }
  }
}
</script>
