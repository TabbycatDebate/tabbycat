<script>
// Subclass should set on the hoverable element:
// @mouseenter="showSlideOver( SUBJECT_DATA )
// @mouseleave="hideSlideOver( SUBJECT_DATA )
// Subclass should usually overrite formatForSlideOver() with their own data
// They pass up an array of 'rows' and an optional annotate method
// The annotate method allows the parent element to append data only it has
// such as conflict lookups

export default {
  data: function () {
    return { slideOverSubject: null }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
  },
  methods: {
    setSlideover: function(object, annotateMethod) {
      var info = object
      if (annotateMethod) {
        var extraFeatures = this[annotateMethod]()
        if (extraFeatures) {
          info['tiers'].push(extraFeatures)
        }
      }
      console.log(info)
      this.slideOverSubject = info
    },
    unsetSlideover: function() {
      this.slideOverSubject = null
    },
    addConflicts: function() {
      return {
        'features': [
          { 'title': 'Test', }
        ]
      }
    }
  }
}
</script>
