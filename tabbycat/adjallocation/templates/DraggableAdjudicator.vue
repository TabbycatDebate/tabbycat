<template>
  <draggable-item :drag-payload="dragPayload"
    :hover-panel="true" :hover-panel-item="adjudicator" :hover-panel-type="'adjudicator'"
    :hover-conflicts="true" :hover-conflicts-item="clashableID" :hover-conflicts-type="'adjudicator'"
    :class="[{'border-light': isTrainee && conflictsCSS === '', 'bg-dark text-white': unavailable },
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
// Note the checks for "this.adjudicator" are a means of coping when an adj is assigned that is not
// in the master list — i.e. those from another tournament or that were added since the page was loaded
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import HighlightableMixin from '../../templates/allocations/HighlightableMixin.vue'
import ConflictableAdjudicatorMixin from '../../templates/allocations/ConflictableAdjudicatorMixin.vue'
import HoverableConflictReceiverMixin from '../../templates/allocations/HoverableConflictReceiverMixin.vue'

export default {
  mixins: [HighlightableMixin, ConflictableAdjudicatorMixin, HoverableConflictReceiverMixin],
  components: { DraggableItem },
  props: {
    item: Object,
    dragPayload: Object,
    debateOrPanelId: Number,
    isTrainee: {
      type: Boolean,
      default: false,
    },
  },
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
      if (this.item && 'id' in this.item) {
        return this.item.id
      }
      return null
    },
    unavailable: function () {
      if (this.doubleAllocated) {
        return true
      } else if (this.item && !this.item.available) {
        return true
      }
      return false
    },
    doubleAllocated: function () {
      if (this.item && 'id' in this.item) {
        return this.$store.getters.duplicateAdjudicatorAllocations.includes(this.item.id)
      }
      return false
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
      if (this.adjudicator && this.adjudicator.institution) {
        const code = this.$store.state.institutions[this.item.institution].code
        var stringDelta = code.length - this.initialledName.length
        if (stringDelta > 3) { // Trim to prevent UI blow outs
          return code.substring(0, this.initialledName.length + 3) + '…'
        }
        return code
      } else {
        return this.gettext('Unaffiliated')
      }
    },
    initialledName: function () {
      // Translate Joe Blogs into Joe B.
      if (!this.adjudicator) {
        return 'Unknown Adj'
      }
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
      if (this.adjudicator) {
        return parseFloat(Math.round(this.adjudicator.score * 100) / 100).toFixed(1)
      }
      return 0
    },
    scoreA: function () {
      return String(this.score)[0] // First digit
    },
    scoreB: function () {
      if (!this.adjudicator) {
        return ''
      } else if (this.adjudicator.score >= 10.0) {
        // For scores with that are double-digits ignore the decimal
        return String(this.score)[1] + '.'
      } else {
        return '.' + String(this.score).split('.')[1]
      }
    },
  },
}
</script>
