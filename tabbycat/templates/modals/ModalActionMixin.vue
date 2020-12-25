<script>
import { mapGetters, mapMutations } from 'vuex'

export default {
  props: { contextOfAction: String },
  computed: {
    ...mapGetters({
      loading: 'loadingState', // Map to the global VueX loading state
    }),
  },
  methods: {
    ...mapMutations({
      setLoading: 'setLoadingState', // Set global loading state
    }),
    resetModal: function () {
      $(this.$refs.modal).modal('hide')
    },
    performWSAction: function (settings = null) {
      this.setLoading(true)
      this.$store.state.wsBridge.send({
        action: this.contextOfAction,
        settings: settings,
      })
    },
  },
  watch: {
    loading: function (newValue, oldValue) {
      if (newValue === false && oldValue === true) {
        this.resetModal() // Hide the modal when loading has finished
      }
    },
  },
}
</script>
