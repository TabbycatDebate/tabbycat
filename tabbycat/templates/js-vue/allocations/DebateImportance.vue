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
  methods: {
    // Call into the ajax mixin
    updateImportance: function() {
      var data = {
          debate_id: this.id,
          importance: this.importance + 2
      }
      this.update(this.url, data, 'debate importance')
    }
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
  }
}
</script>
