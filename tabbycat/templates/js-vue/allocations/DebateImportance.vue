<template>
  <td>
    <span class="hidden">
      {{ importance }}
    </span>
    <input max="2" min="-2" step="1" type="range" v-model="importance">
    <span class="small text-center">
      {{ importance }}
    </span>
  </td>
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
  }
}
</script>
