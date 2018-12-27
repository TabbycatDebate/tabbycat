<template>
  <draggable-item :drag-payload="dragPayload"
    :hover-panel="true" :hover-panel-item="adjudicator" :hover-panel-type="'adjudicator'"
    :hover-conflicts="true" :hover-conflicts-item="adjudicator.id" :hover-conflicts-type="'adjudicator'"
    :class="[{'border-light': isTrainee && conflictsCSS === '',
              'bg-dark text-white': !item.available || doubleAllocated },
              highlightsCSS, conflictsCSS, hoverConflictsCSS]">

    <span slot="number">
      <small class="pl-2 vue-draggable-muted ">{{ scoreA }}{{ scoreB }}</small>
    </span>
    <span slot="title">
      {{ initialledName }}
    </span>
    <span slot="subtitle">
      {{ institutionCode }}
    </span>
    <div slot="tooltip" class="history-tooltip tooltip" v-if="hasHistory">
      <div :class="['tooltip-inner conflictable', 'hover-histories-' + hasHistory + '-ago']">
        {{ hasHistory }} ago
      </div>
    </div>

  </draggable-item>
</template>

<script>
import DraggableItem from '../../utils/templates/DraggableItem.vue'
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import ConflictableAdjudicatorMixin from '../../utils/templates/ConflictableAdjudicatorMixin.vue'
import HoverableConflictReceiverMixin from '../../utils/templates/HoverableConflictReceiverMixin.vue'

export default {
  mixins: [HighlightableMixin, ConflictableAdjudicatorMixin, HoverableConflictReceiverMixin],
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false, debateOrPanelId: Number },
  computed: {
    highlightData: function () {
      return this.adjudicator
    },
    adjudicator: function () {
      return this.item
    },
    clashableType: function () {
      return 'adjudicator'
    },
    clashableID: function () {
      return this.item.id
    },
    doubleAllocated: function () {
      return this.$store.getters.duplicateAdjudicatorAllocations.includes(this.item.id)
    },
    hasHistory: function () {
      if (this.hasHoverHistoryConflict) {
        return this.hasHoverHistoryConflict
      } else if (this.hasHistoryConflict) {
        return this.hasHistoryConflict
      }
      return false
    },
    institutionCode: function () {
      if (this.adjudicator.institution) {
        return this.$store.state.institutions[this.adjudicator.institution].code
      } else {
        return this.gettext('Unaffiliated')
      }
    },
    initialledName: function () {
      // Translate Joe Blogs into Joe B.
      const names = this.adjudicator.name.split(' ')
      if (names.length > 1) {
        const lastname = names[names.length - 1]
        const lastInitial = lastname[0]
        let firstNames = this.adjudicator.name.split(` ${lastname}`).join('')
        const limit = 10
        if (firstNames.length > limit + 2) {
          firstNames = `${firstNames.substring(0, limit)}…`
        }
        return `${firstNames} ${lastInitial}`
      }
      return names.join(' ')
    },
    score: function () {
      // Scores can come through as integers; need to ensure they are re-rounded
      return parseFloat(Math.round(this.adjudicator.score * 100) / 100).toFixed(1)
    },
    scoreA: function () {
      return String(this.score)[0] // First digit
    },
    scoreB: function () {
      if (this.adjudicator.score >= 10.0) {
        // For scores with that are double-digits ignore the decimal
        return String(this.score)[1] + '.'
      } else {
        return '.' + String(this.score).split('.')[1]
      }
    },
  },
}
</script>
