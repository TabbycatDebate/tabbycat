<script>
// Basically just spun out of the Edit Adjs container
// Assumes data objects for teams/adjs/unallocated
import _ from 'lodash'

export default {
  created: function () {
    this.$eventHub.$on('set-highlights', this.setHighlights)
  },
  methods: {
    setHighlights (highlights) {
      // Highlights come in as more expansive dictionary;
      // reduce them back to a simple key/state
      const simpleHighlights = _.mapValues(highlights, highlight => highlight.state)

      this.teams.forEach((item) => {
        item.highlights = simpleHighlights
      })
      this.adjudicators.forEach((item) => {
        item.highlights = simpleHighlights
      })
      this.unallocatedItems.forEach((item) => {
        item.highlights = simpleHighlights
      })
    },
  },
}
</script>
