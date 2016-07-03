<script>
// Inheritors should trigger showConflictHighlights / hideConflictHighlights
// from some form of action
// Their classes should be set by binding conflictsHighlights somewhere
// Must provide an entity that has an ID property to match with conflicts

export default {
  props: {
    debateId: Number,
  },
  methods: {
    setHistoriesHighlights: function() {
      this.$dispatch('set-histories', this.entity.histories)
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
        var entity = this.entity;
        var match = '';

        // Redo the below to be team or adj agnostic
        // // Search for first matching adj element
        // if (this.getEntity()[1] === 'adj') {
        //   for (var i=0, iLen=histories.length; i<iLen; i++) {
        //     if (histories[i].adj == entity.id) {
        //       match = 'histories-display seen-' + histories[i].ago + '-ago';
        //       break;
        //     }
        //   }
        // }
        // // Search for first matching team element
        // if (this.getEntity()[1] === 'team') {
        //   for (var i=0, iLen=histories.length; i<iLen; i++) {
        //     if (histories[i].team == entity.id) {
        //       match = 'histories-display seen-' + histories[i].ago + '-ago';
        //       break;
        //     }
        //   }
        // }
        // return match;

      }
    }
  }
}
</script>
