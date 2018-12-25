<template>
  <div class="text-truncate small py-1 px-2 inline-team flex-fill d-flex align-items-center"
       :class="[highlightsCSS, conflictsCSS]"
       @mouseenter="showHoverPanel(team, 'team')" @mouseleave="hideHoverPanel">
    <div>
      {{ team.short_name }}
    </div>
  </div>
</template>

<script>
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverableMixin from '../../utils/templates/HoverableMixin.vue'
import ConflictableTeamMixin from '../../utils/templates/ConflictableTeamMixin.vue'

export default {
  mixins: [HighlightableMixin, HoverableMixin, ConflictableTeamMixin],
  props: { team: Object, debateId: Number },
  computed: {
    highlightData: function () {
      return this.team
    },
  },
}
</script>

<style scoped>
  .inline-team {
    height: 100%; /* Need to fill space */
  }
  .inline-team.conflictable {
    border-width: 5px; /* For conflicts */
    border-style: solid;
  }
</style>
