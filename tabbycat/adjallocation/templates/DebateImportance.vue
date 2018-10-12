<template>
  <div @mouseover="showTooltip=true" @mouseleave="showTooltip=false">

    <input max="2" min="-2" step="1" type="range" v-model.number.lazy="importance">
    <div class="tooltip bottom tooltip-vue" role="tooltip" v-if="showTooltip">
      <div class="tooltip-arrow"></div>
      <div class="tooltip-inner">{{ importanceDescription }}</div>
    </div>

  </div>
</template>

<script>

export default {
  mixins: [],
  data: function () {
    return { showTooltip: false }
  },
  props: {
    importance: Number, id: Number,
  },
  computed: {
    importanceDescription: function () {
      if (this.internalImportance === 2) {
        return 'V.I.P.'
      } else if (this.internalImportance === 1) {
        return 'Important'
      } else if (this.internalImportance === 0) {
        return 'Neutral'
      } else if (this.internalImportance === -1) {
        return 'Unimportant'
      } else if (this.internalImportance === -2) {
        return '¯\\_(ツ)_/¯'
      }
      return null
    },
  },
}
</script>
