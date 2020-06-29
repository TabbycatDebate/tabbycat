<script>
// Provides shared functionality common across the container components for editing
// adjs/teams/venues etc
import { mapGetters } from 'vuex'

import DragAndDropDebate from '../../templates/allocations/DragAndDropDebate.vue'
import DragAndDropLayout from '../../templates/allocations/DragAndDropLayout.vue'
import DragAndDropActions from '../../templates/allocations/DragAndDropActions.vue'
import WebsocketMixin from '../../templates/ajax/WebSocketMixin.vue'

export default {
  mixins: [WebsocketMixin],
  components: { DragAndDropDebate, DragAndDropLayout, DragAndDropActions },
  props: ['initialData'],
  data: function () {
    return {
      sockets: ['debates'],
    }
  },
  created: function () {
    // Initial mutation to the Vuex store that sets up the initial state
    this.$store.commit('setupInitialData', this.initialData)
    this.$store.commit('setupWebsocketBridge', this.bridges[this.sockets[0]])
  },
  computed: {
    ...mapGetters(['allDebatesOrPanels', 'sortedDebatesOrPanels']),
    debatesOrPanelsCount: function () {
      return Object.keys(this.allDebatesOrPanels).length
    },
    tournamentSlugForWSPath: function () {
      return this.initialData.tournament.slug
    },
    roundSlugForWSPath: function () {
      return this.initialData.round.seq
    },
    unallocatedItems: function () {
      // Filters the global list of items based upon the state of each individual debate
      const allocatedItemIDs = []
      const allDebatesOrPanels = this.$store.getters.allDebatesOrPanels
      for (const keyPanel of Object.entries(allDebatesOrPanels)) {
        allocatedItemIDs.push(...this.getUnallocatedItemFromDebateOrPanel(keyPanel[1]))
      }
      const unallocatedItems = []
      const allUnallocatedItems = this.$store.getters.allocatableItems
      for (const [id, adjudicator] of Object.entries(allUnallocatedItems)) {
        if (!allocatedItemIDs.includes(Number(id))) {
          unallocatedItems.push(adjudicator)
        }
      }
      return unallocatedItems
    },
  },
  methods: {
    handleSocketReceive: function (socketLabel, payload) {
      this.$store.dispatch('receiveUpdatedupdateDebatesOrPanelsAttribute', payload)
    },
    showAllocate: function () {
      $('#confirmAllocateModal').modal('show')
    },
    showPrioritise: function () {
      $('#confirmPrioritiseModal').modal('show')
    },
  },
}
</script>
