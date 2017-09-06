<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData.available }}
    </span>
    <input type="checkbox" v-model="cellData.available" @click="checkUpdate">
    av: {{ cellData.available }}

  </td>

</template>

<script>
import AjaxMixin from '../js-vue/ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    cellData: Object,
  },
  computed: {
    breaking: function() {
      return this.cellData.breaking
    }
  },
  methods: {
    checkUpdate: function () {
      var cd = this.cellData
      var message = "availability type " + cd.id + "'s availability status as " + cd.available
      var payload = { 'breaking': cd.breaking, id: cd.id }
      this.ajaxSave(cd.saveURL, payload, message, null, null, null)
    },
  },
}

</script>