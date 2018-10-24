<template>
  <draggable-item :drag-payload="dragPayload" :class="{ 'border-light': isTrainee }">

      <span slot="number">
        <small class="vue-draggable-muted ">{{ scoreInt }}.{{ scoreDecimal }}</small>
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

export default {
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false },
  computed: {
    adjudicator: function () {
      return this.item
    },
    institutionCode: function () {
      if (this.adjudicator.institution) {
        return this.$store.state.institutions[this.adjudicator.institution].code
      } else {
        return 'Unaffiliated'
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
    scoreInt: function () {
      return String(this.score).split('.')[0]
    },
    scoreDecimal: function () {
      return String(this.score).split('.')[1]
    },
  },
}
</script>
