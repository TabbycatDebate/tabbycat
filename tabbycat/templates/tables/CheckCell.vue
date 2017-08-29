<template>

  <td :class="cellData['class'] ? cellData['class'] : null" @click="saveBreaking">

    <span v-if="cellData['sort']" hidden>
      {{ cellData["sort"] }} <!-- Sorting key -->
    </span>
    <input type="checkbox" v-model="cellData.breaking">

  </td>

</template>

<script>
import AjaxMixin from '../js-vue/ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    cellData: Object,
  },
  methods: {
    saveBreaking: function (event) {
      var cd = this.cellData
      var message = "adj " + cd.id + "'s break status as " + cd.breaking
      var payload = { 'breaking': cd.breaking, id: cd.id }
      this.ajaxSave(cd.saveURL, payload, message, null, null, null)
    },
  }
}

</script>