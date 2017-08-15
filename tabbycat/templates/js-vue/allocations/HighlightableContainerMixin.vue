<script>
// Basically just spun out of the Edit Adjs container
// Assumes data objects for teams/adjs/unallocated
import _ from 'lodash'

export default {
  created: function() {
    this.$eventHub.$on('set-highlights', this.setHighlights)
  },
  computed: {

  },
  methods: {
    setHighlights(highlights) {
      _.forEach(this.debateTeams, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.debateAdjudicators, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.unallocatedItems, function(item) {
        item.highlights = highlights
      })
    }
  }
}
</script>
