<template>
  <div @mouseover="showTooltip = true" @mouseleave="showTooltip = false">

    <input max="2" min="-2" step="1" type="range"
           v-model.number="internalImportance">

    <div class="tooltip bottom tooltip-vue" role="tooltip" v-if="showTooltip">
      <div class="tooltip-arrow"></div>
      <div class="tooltip-inner">{{ importanceDescription }}</div>
    </div>

  </div>
</template>

<script>
import AjaxMixin from '../AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  data: function() {
    return { showTooltip: false, internalImportance: null, initiallySet: false  }
  },
  props: {
    importance: Number, id: Number
  },
  created: function() {
    // We initially sync the internalValue with the value passed in by the parent
    this.internalImportance = this.importance;
    this.initiallySet = true
  },
  computed: {
    importanceDescription: function() {
      if (this.internalImportance === 2) {
        return "V.I.P."
      } else if (this.internalImportance === 1) {
        return "Important"
      } else if (this.internalImportance === 0) {
        return "Neutral"
      } else if (this.internalImportance === -1) {
        return "Unimportant"
      } else if (this.internalImportance === -2) {
        return "¯\\_(ツ)_/¯"
      }
    }
  },
  watch: {
    'internalImportance': function() {
      if (this.internalImportance !== this.importance) {
        // Only update if an actual change has occured
        console.log('saving importance to parent')
        this.$eventHub.$emit('update-importance', this.id, this.internalImportance)
      }
    }
  }
}
</script>
