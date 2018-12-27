<template>
  <div class="text-truncate small py-1 px-2 inline-team flex-fill d-flex align-items-center hover-target"
       :class="[highlightsCSS, conflictsCSS]"
       @mouseenter="showHoverPanel(team, 'team')" @mouseleave="hideHoverPanel">
    <div :class="[this.isLive ? '' : 'not-live']">
      {{ team.short_name }}
    </div>
    <div class="history-tooltip tooltip" v-if="hasHistoryConflict">
      <div :class="['tooltip-inner conflictable', 'hover-histories-' + hasHistoryConflict + '-ago']">
        {{ hasHistoryConflict }} ago
      </div>
    </div>
  </div>
</template>

<script>
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverablePanelMixin from '../../utils/templates/HoverablePanelMixin.vue'
import ConflictableTeamMixin from '../../utils/templates/ConflictableTeamMixin.vue'

export default {
  mixins: [HighlightableMixin, HoverablePanelMixin, ConflictableTeamMixin],
  props: { team: Object, debateId: Number },
  computed: {
    highlightData: function () {
      return this.team
    },
    isLive: function () {
      for (let bc of this.team.break_categories) {
        let category = this.highlights.break.options[bc]
        if (category) {
          if (this.team.points >= category.fields.safe) {
            return true
          } else if (this.team.points <= category.fields.dead) {
            return false
          } else if (this.team.points > category.fields.dead && this.team.points < category.fields.safe) {
            return true
          }
        }
      }
      return true // Default for pages which don't calculate it
    },
  },
}
</script>
