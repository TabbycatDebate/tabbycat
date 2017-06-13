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
      _.forEach(this.teams, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.adjudicators, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.unallocatedItems, function(item) {
        item.highlights = highlights
      })
    }
  }
}
</script>
