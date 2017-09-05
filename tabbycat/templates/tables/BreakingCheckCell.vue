<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData.breaking }}
    </span>
    <input type="checkbox" v-model="cellData.breaking" @click="checkUpdate">

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
      var message = "adj " + cd.id + "'s break status as " + cd.breaking
      var payload = { 'breaking': cd.breaking, id: cd.id }
      this.ajaxSave(cd.saveURL, payload, message, null, null, null)
    },
  },
}

</script>