<template>
  <div class="text-truncate small px-1 inline-team flex-fill d-flex align-items-center hover-target"
       :class="[highlightsCSS, conflictsCSS, hoverConflictsCSS]"
       @mouseenter="showHovers" @mouseleave="hideHovers">
    <div :class="[this.isLive ? '' : 'not-live']" v-text="teamName"></div>
    <div class="history-tooltip tooltip" v-if="hasHistory">
      <div :class="['tooltip-inner conflictable', 'hover-histories-' + hasHistory + '-ago']">
        {{ hasHistory }} ago
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import HighlightableMixin from '../../templates/allocations/HighlightableMixin.vue'
import HoverablePanelMixin from '../../templates/allocations/HoverablePanelMixin.vue'
import HoverableConflictMixin from '../../templates/allocations/HoverableConflictMixin.vue'
import HoverableConflictReceiverMixin from '../../templates/allocations/HoverableConflictReceiverMixin.vue'
import ConflictableTeamMixin from '../../templates/allocations/ConflictableTeamMixin.vue'

export default {
  mixins: [HighlightableMixin, HoverablePanelMixin, HoverableConflictMixin, HoverableConflictReceiverMixin, ConflictableTeamMixin],
  props: { team: Object, debateId: Number, isElimination: Boolean },
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
    teamName: function () {
      let name = this.team.short_name // Default
      if (this.extra.codeNames === 'everywhere' || this.extra.codeNames === 'admin-tooltips-real') {
        name = this.team.code_name
        if (name === '') {
          name = this.gettext('No code name set')
        }
      }
      return name
    },
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
      if (this.isElimination || this.team.break_categories.length === 0) {
        return true // Never show strikeouts in out rounds; don't show if no categories are set
      }
      const breakCategoriesCount = this.team.break_categories.length
      let letDeadCategoriesCount = 0
      for (const bc of this.team.break_categories) {
        const category = this.highlights.break.options[bc]
        if (category) {
          if (this.team.points >= category.fields.safe) {
            letDeadCategoriesCount += 1
          }
          if (this.team.points <= category.fields.dead) {
            letDeadCategoriesCount += 1
          }
        }
      }
      return (breakCategoriesCount - letDeadCategoriesCount) > 0
    },
    ...mapState(['extra']),
  },
}
</script>
