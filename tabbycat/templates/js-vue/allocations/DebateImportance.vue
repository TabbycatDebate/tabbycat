<template>
  <div>
    <input max="2" min="-2" step="1" type="range" v-model="importance">
    <div class="small text-center text-muted">
      {{ importanceDescription }}
    </div>
  </div>
</template>

<script>
import AjaxMixin from '../mixins/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    id: Number,
    importance: Number,
    url: String,
  },
  computed: {
    importanceDescription: function() {
      if (this.importance === 2) {
        return "VIP"
      } else if (this.importance === 1) {
        return "Important"
      } else if (this.importance === 0) {
        return "Neutral"
      } else if (this.importance === -1) {
        return "Unimportant"
      } else if (this.importance === -2) {
        return "¯\\_(ツ)_/¯"
      }
    }
  },
  watch: {
    'importance': function (newVal, oldVal) {
      var data = {
          debate_id: this.id,
          importance: this.importance
      }
      this.update(this.url, data, 'debate ' + this.id + '\'s importance')
    }
  }
}
</script>
