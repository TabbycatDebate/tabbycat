<script>
// Provides shared functionality common across the container components for editing
// adjs/teams/venues etc
import DragAndDropDebate from '../../utils/templates/DragAndDropDebate.vue'
import WebsocketMixin from '../../templates/ajax/WebSocketMixin.vue'

export default {
  mixins: [WebsocketMixin],
  components: { DragAndDropDebate },
  props: ['initialDebatesOrPanels', 'initialRoundInfo'],
  data: function () {
    return {
      sockets: ['debates'],
    }
  },
  created: function () {
    // Initial mutation to the Vuex store that sets up the initial state
    this.$store.commit('setupDebatesOrPanels', this.initialDebatesOrPanels)
    this.$store.commit('setupRoundInfo', this.initialRoundInfo)
    this.$store.commit('setupWebsocketBridge', this.bridges[this.sockets[0]])
  },
  computed: {
    debatesOrPanels () {
      return this.$store.getters.allDebatesOrPanels
    },
    tournamentSlugForWSPath: function () {
      return this.initialRoundInfo.tournamentSlug
    },
    roundSlugForWSPath: function () {
      return this.initialRoundInfo.roundSeq
    },
  },
  methods: {
    handleSocketReceive: function (socketLabel, payload) {
      this.$store.dispatch('receiveUpdatedupdateDebatesOrPanelsAttribute', payload)
    },
  },
}
</script>
