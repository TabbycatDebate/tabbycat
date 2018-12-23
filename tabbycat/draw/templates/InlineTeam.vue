<template>
  <div class="text-truncate small py-1 px-2 flex-fill" :class="highlightsCSS"
       @mouseenter="showHoverPanel(team, 'team')" @mouseleave="hideHoverPanel">
    {{ team.short_name }}
  </div>
</template>

<script>
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverableMixin from '../../utils/templates/HoverableMixin.vue'

export default {
  mixins: [HighlightableMixin, HoverableMixin],
  props: { team: Object },
  computed: {
    highlightData: function () {
      return this.team
    },
  },
}
</script>
