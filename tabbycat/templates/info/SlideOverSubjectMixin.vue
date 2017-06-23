<script>
// Subclass should set on the hoverable element:
// @mouseenter="showSlideOver( SUBJECT_DATA )
// @mouseleave="hideSlideOver( SUBJECT_DATA )
// Subclass should usually overrite formatForSlideOver() with their own data

export default {
  methods: {
    showSlideOver: function(event, subject) {
      this.$eventHub.$emit('set-slideover', this.formatForSlideOver(subject),
                                            this.annotateMethodForSlideOver())
    },
    hideSlideOver: function(event) {
      this.$eventHub.$emit('unset-slideover')
    },
    formatForSlideOver: function(subject) {
      return subject // Children should override
    },
    annotateMethodForSlideOver: function() {
      return null // Children should pass a string that corresponds to a
                  // function to be called on the Container
    }
  }
}
</script>
