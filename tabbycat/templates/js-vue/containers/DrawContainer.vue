<script>
export default {
  data: function() {
    return { slideSubject: null, slideInfo: null }
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
    annotateSlideInfo: function() {
      return null; // Subclasses should implement own method to add data
    },
    setSlideover: function(object) {
      this.slideSubject = object
      this.slideInfo = this.annotateSlideInfo(object)
    },
    unsetSlideover: function() {
      // this.slideSubject = null
      // this.slideConstraints = null
    },
  }
}
</script>