<script>
// Must set action of @mouseenter="showHoverPanel( SUBJECT_DATA, SUBJECT_TYPE )
// Must set action of @mouseleave="hideHoverPanel( SUBJECT_DATA, SUBJECT_TYPE )
import { mapMutations } from 'vuex'

export default {
  methods: {
    showHoverPanel: function (subject, type) {
      this.setHoverPanel({ subject: subject, type: type })
    },
    hideHoverPanel: function () {
      this.unsetHoverPanel()
    },
    ...mapMutations(['setHoverPanel', 'unsetHoverPanel']),
  },
}
</script>
