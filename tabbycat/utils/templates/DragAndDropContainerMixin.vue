<script>
// Provides shared functionality common across the container components for editing
// adjs/teams/venues etc
import DragAndDropDebate from '../../utils/templates/DragAndDropDebate.vue'

export default {
  components: { DragAndDropDebate },
  props: ['initialDebatesOrPanels', 'initialRoundInfo'],
  created: function () {
    // Initial mutation to the Vuex store that sets up the initial state
    this.$store.commit('setupDebatesOrPanels', this.initialDebatesOrPanels)
    this.$store.commit('setupRoundInfo', this.initialRoundInfo)
  },
  computed: {
    debatesOrPanels () {
      return this.$store.getters.allDebatesOrPanels
    },
  },
}
</script>
