<script>
// Note the data/props/computed setup as per https://vuejs.org/v2/guide/components.html
// Props are passed down from root; but we need to cast them into data
// so that it can then mutate them here in response to children

export default {
  data: function () {
    return {
      slideOverItem: null,
      debates: this.initialDebates,
      unallocatedItems: this.initialUnallocatedItems
    }
  },
  props: ['initialDebates', 'initialUnallocatedItems'],
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