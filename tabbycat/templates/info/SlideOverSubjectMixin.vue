<script>
// Subclass should set on the hoverable element:
// @mouseenter="showSlideOver( SUBJECT_DATA )
// @mouseleave="hideSlideOver( SUBJECT_DATA )
// Subclass should usually overrite formatForSlideOver() with their own data

export default {
  data: function () {
    // Children should pass a string that corresponds to a function to be called on the Container
    return { annotationMethodName: null }
  },
  methods: {
    showSlideOver: function (event, subject) {
      var slide = this.formatForSlideOver(subject)
      var annotationCall = this.annotationMethodName
      var annotationItem = this.annotateDataForSlideOver
      this.$eventHub.$emit('set-slideover', slide, annotationCall, annotationItem)
    },
    hideSlideOver: function (event) {
      this.$eventHub.$emit('unset-slideover')
    },
    formatForSlideOver: function (subject) {
      return subject // Children should override
    },
  },
  computed: {
    annotateDataForSlideOver: function () {
      return null  // Children should return an object that can be used by
                  // annotateMethodForSlideOver; such as a conflictable adj
    }
  }
}
</script>
