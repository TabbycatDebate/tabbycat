<template>
  <div class="text-truncate small px-1 inline-team flex-fill d-flex align-items-center hover-target"
       :class="[highlightsCSS, conflictsCSS, hoverConflictsCSS]"
       @mouseenter="showHovers" @mouseleave="hideHovers">
    <div :class="[this.isLive ? '' : 'not-live']">
      {{ team.short_name }}
    </div>
    <div class="history-tooltip tooltip" v-if="hasHistory">
      <div :class="['tooltip-inner conflictable', 'hover-histories-' + hasHistory + '-ago']">
        {{ hasHistory }} ago
      </div>
    </div>
  </div>
</template>

<script>
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverablePanelMixin from '../../utils/templates/HoverablePanelMixin.vue'
import HoverableConflictMixin from '../../utils/templates/HoverableConflictMixin.vue'
import HoverableConflictReceiverMixin from '../../utils/templates/HoverableConflictReceiverMixin.vue'
import ConflictableTeamMixin from '../../utils/templates/ConflictableTeamMixin.vue'

export default {
  mixins: [HighlightableMixin, HoverablePanelMixin, HoverableConflictMixin, HoverableConflictReceiverMixin, ConflictableTeamMixin],
  props: { team: Object, debateId: Number },
  methods: {
    showHovers: function () {
      this.showHoverPanel(this.team, 'team')
      this.showHoverConflicts(this.team.id, 'team')
    },
    hideHovers: function () {
      this.hideHoverPanel()
      this.hideHoverConflicts()
    },
  },
  computed: {
    clashableType: function () {
      return 'team'
    },
    clashableID: function () {
      return this.team.id
    },
    highlightData: function () {
      return this.team
    },
    hasHistory: function () {
      if (this.hasHoverHistoryConflict) {
        return this.hasHoverHistoryConflict
      } else if (this.hasHistoryConflict) {
        return this.hasHistoryConflict
      }
      return false
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
