<script>
// Basically just spun out of the Edit Adjs container
// Assumes data objects for teams/adjs/unallocated
import _ from 'lodash'

export default {
  created: function () {
    this.$eventHub.$on('set-highlights', this.setHighlights)
  },
  methods: {
    setHighlights(highlights) {
      // Highlights come in as more expansive dictionary;
      // reduce them back to a simple key/state
      var simpleHighlights = _.mapValues(highlights, function (highlight) {
        return highlight.state;
      });
      console.log(simpleHighlights)
      _.forEach(this.teams, function (item) {
        item.highlights = simpleHighlights
      })
      _.forEach(this.adjudicators, function (item) {
        item.highlights = simpleHighlights
      })
      _.forEach(this.unallocatedItems, function (item) {
        item.highlights = simpleHighlights
      })
    }
  }
}
</script>
