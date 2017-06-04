<script>
// Subclass should set on the hoverable element:
// v-on:mouseenter="showSlideOver( SUBJECT_DATA )
// v-on:mouseleave="hideSlideOver( SUBJECT_DATA )

export default {
  props: {
  },
  computed: {
  },
  methods: {
    showSlideOver: function(event, subjectData) {
      this.$eventHub.$emit('set-slideover', subjectData)
    },
    hideSlideOver: function(event) {
      this.$eventHub.$emit('unset-slideover')
    },
  }
}
</script>
