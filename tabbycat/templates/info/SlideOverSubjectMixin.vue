<script>
// Subclass should set on the hoverable element:
// @mouseenter="showSlideOver( SUBJECT_DATA )
// @mouseleave="hideSlideOver( SUBJECT_DATA )
// Subclass should usually overrite formatForSlideOver() with their own data


export default {
  props: {
  },
  computed: {
  },
  methods: {
    showSlideOver: function(event, subject) {
      this.$eventHub.$emit('set-slideover', this.formatForSlideOver(subject))
    },
    hideSlideOver: function(event) {
      this.$eventHub.$emit('unset-slideover')
    },
    formatForSlideOver: function(subject) {
      return subject
    }
  }
}
</script>
