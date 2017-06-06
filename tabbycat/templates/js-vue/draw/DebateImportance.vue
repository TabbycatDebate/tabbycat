<template>
  <div @mouseover="showTooltip = true" @mouseleave="showTooltip = false">

    <input max="2" min="-2" step="1" type="range"
           v-model.number="setImportance" type="number">

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
    return { setImportance: null,
             showTooltip: false }
  },
  props: {
    importance: Number,
    id: Number,
    url: String,
  },
  computed: {
    importanceDescription: function() {
      if (this.setImportance === 2) {
        return "V.I.P."
      } else if (this.setImportance === 1) {
        return "Important"
      } else if (this.setImportance === 0) {
        return "Neutral"
      } else if (this.setImportance === -1) {
        return "Unimportant"
      } else if (this.setImportance === -2) {
        return "¯\\_(ツ)_/¯"
      }
    }
  },
  created: function() {
    this.setImportance = this.importance
  },
  watch: {
    'setImportance': function (newVal, oldVal) {
      console.log('saving importance')
      var ajaxData = {
        debate_id: this.id,
        importance: this.importance
      }
      //this.update(this.url, ajaxData, 'debate ' + this.id + '\'s importance')
    }
  }
}
</script>
