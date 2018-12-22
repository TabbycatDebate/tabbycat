<template>
  <div class="text-truncate small py-1 px-2 flex-fill" :class="highlightsCSS">
    {{ team.short_name }}
  </div>
</template>

<script>
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'

export default {
  mixins: [HighlightableMixin],
  props: { team: Object },
  computed: {
    highlightData: function () {
      return this.team
    },
  },
}
</script>
