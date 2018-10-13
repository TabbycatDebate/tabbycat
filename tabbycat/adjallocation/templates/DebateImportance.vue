<template>
  <div @mouseover="showTooltip=true" @mouseleave="showTooltip=false">

    <input max="2" min="-2" step="1" type="range" v-model="importance">
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
  props: { debateOrPanel: Object },
  computed: {
    importanceDescription: function () {
      if (this.debateOrPanel.importance === 2) {
        return 'V.I.P.'
      } else if (this.debateOrPanel.importance === 1) {
        return 'Important'
      } else if (this.debateOrPanel.importance === 0) {
        return 'Neutral'
      } else if (this.debateOrPanel.importance === -1) {
        return 'Unimportant'
      } else if (this.debateOrPanel.importance === -2) {
        return '¯\\_(ツ)_/¯'
      }
      return null
    },
    importance: {
      get () {
        return this.debateOrPanel.importance
      },
      set (value) {
        // Pass a message to the parent component to then save a change to the store
        let updatedDebatesOrPanels = { }
        updatedDebatesOrPanels[this.debateOrPanel.id] = { 'importance': value }
        this.$store.dispatch('updateDebatesOrPanelsAttribute', updatedDebatesOrPanels)
      },
    },
  },
}
</script>
