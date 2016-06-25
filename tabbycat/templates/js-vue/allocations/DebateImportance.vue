<template>
  <td>
    <span class="hidden">
      {{ componentData.importance }}
    </span>
    <select class="form-control input-sm" v-model="componentData.importance" v-on:change="updateImportance">
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
    componentData: Object,
  },
  methods: {
    // Call into the ajax mixin
    updateImportance: function() {
      var data = {
          debate_id: this.componentData.id,
          importance: this.componentData.importance
      }
      this.update(this.componentData.url, data, 'debate importance')
    }
  }
}
</script>
