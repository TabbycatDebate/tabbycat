<script>
// Note the data/props/computed setup as per https://vuejs.org/v2/guide/components.html
// Props are passed down from root; but we need to cast them into data
// so that it can then mutate them here in response to children
import _ from 'lodash'

export default {
  data: function () {
    return {
      slideOverItem: null,
      debates: this.initialDebates,
      unallocatedItems: this.initialUnallocatedItems
    }
  },
  props: ['initialDebates', 'initialUnallocatedItems', 'backUrl'],
  computed: {
    teams: function() {
      // Return all teams as a single array
      var allTeams = _.map(this.debates, function(debate) {
        return debate.teams
      })
      return _.flattenDeep(allTeams)
    },
    adjudicators: function() {
      var allPanellists = _.map(this.debates, function(debate) {
        return _.map(debate.panel, function(panel) {
          return panel.adjudicator
        })
      })
      return _.flattenDeep(allPanellists)
    },
    positions: function() {
      return this.debates[0].positions // Shortcut function
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
    this.$eventHub.$on('unassign-draggable', this.moveToUnused)
  },
  methods: {
    setSlideover: function(object) {
      this.slideOverItem = object
    },
    unsetSlideover: function() {
      this.slideOverItem = null
    },
  }
}
</script>