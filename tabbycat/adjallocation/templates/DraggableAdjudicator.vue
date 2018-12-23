<template>
  <draggable-item :drag-payload="dragPayload"
    :enable-hover="true" :hover-item="hoverableData" :hover-type="hoverableType"
    :class="[highlightsCSS, { 'border-light': isTrainee, 'bg-dark text-white': !item.available }]">

    <span slot="number">
      <small class="pl-2 vue-draggable-muted ">{{ scoreA }}{{ scoreB }}</small>
    </span>
    <span slot="title">
      {{ initialledName }}
    </span>
    <span slot="subtitle">
      {{ institutionCode }}
    </span>

  </draggable-item>
</template>

<script>
import DraggableItem from '../../utils/templates/DraggableItem.vue'
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverableMixin from '../../utils/templates/HoverableMixin.vue'

export default {
  mixins: [HoverableMixin, HighlightableMixin],
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false },
  computed: {
    highlightData: function () {
      return this.adjudicator
    },
    hoverableData: function () {
      return this.adjudicator
    },
    hoverableType: function () {
      return 'adjudicator'
    },
    adjudicator: function () {
      return this.item
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
