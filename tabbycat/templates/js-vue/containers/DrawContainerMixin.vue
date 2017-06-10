<script>
// Note the data/props/computed setup as per https://vuejs.org/v2/guide/components.html
// Props are passed down from root; but we need to cast them into data
// so that it can then mutate them here in response to children
import AjaxMixin from '../draganddrops/AjaxMixin.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import SlideOverItem from '../infoovers/SlideOverItem.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: {
    DrawHeader, AutoSaveCounter, Debate,
    DroppableGeneric, UnallocatedItemsContainer, SlideOverItem
  },
  data: function () {
    return {
      slideOverItem: null,
      debates: this.initialDebates,
      unallocatedItems: this.initialUnallocatedItems
    }
  },
  props: ['initialDebates', 'initialUnallocatedItems', 'roundInfo'],
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
    this.$eventHub.$on('unassign-draggable', this.moveToUnused)
    this.$eventHub.$on('assign-draggable', this.moveToDebate)
    this.$eventHub.$on('update-allocation', this.updateDebates)
    this.$eventHub.$on('update-unallocated', this.updateUnallocatedItems)
  },
  computed: {
    teams: function() {
      // Return all teams as a single array
      var allTeams = _.map(this.debates, function(debate) {
        return _.map(debate.teams, function(team) {
          return team.team
        })
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
    debatesById: function() {
      return _.keyBy(this.debates, 'id')
    },
    teamsById: function() {
      return _.keyBy(this.teams, 'id')
    },
    adjudicatorsById: function() {
      return _.keyBy(this.adjudicators, 'id')
    },
    positions: function() {
      return this.debates[0].positions // Shortcut function
    }
  },
  methods: {
    setSlideover: function(object) {
      this.slideOverItem = object
    },
    unsetSlideover: function() {
      this.slideOverItem = null
    },
    updateDebates: function(updatedDebates) {
      this.debates = updatedDebates // Match internal data to json response
    },
    updateUnallocatedItems: function(updatedUnallocatedItems) {
      this.unallocatedItems = updatedUnallocatedItems // As above
    },
  }
}
</script>