<script>
export default {
  data: function() {
    return { slideOverItem: null }
  },
  props: {
    debates: Array,
    unallocatedItems: Array
  },
  computed: {
    positions: function() {
      return this.debates[0].positions // Shortcut function
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
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