<template>
  <td>
    <span class="hidden">
      {{ importance }}
    </span>
    <select class="form-control input-sm" v-model="importance" v-on:change="updateImportance">
      <option value="1">1</option>
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="4">4</option>
      <option value="5">5</option>
    </select>
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
          importance: this.importance
      }
      this.update(this.url, data, 'debate importance')
    }
  }
}
</script>
