<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData.checked }}
    </span>
    <label class="custom-control custom-checkbox">
      <input type="checkbox" class="custom-control-input" v-model="cellData.checked">
      <span class="custom-control-indicator"></span>
    </label>

  </td>

</template>

<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  props: {
    cellData: Object,
  },
  computed: {
    checked: function() {
      return this.cellData.checked
    }
  },
  watch: {
    'cellData.checked': function (val, oldVal) {
      if (_.isUndefined(this.cellData.saveURL)) {
        this.$eventHub.$emit('toggle-checked', this.cellData.id,
                                               this.cellData.checked)
      } else {
        var cd = this.cellData
        var message = "adj " + cd.id + "'s " + cd.type + " status as " + cd.checked
        var payload = { id: cd.id }
        payload[cd.type] = cd.checked
        this.ajaxSave(cd.saveURL, payload, message, null, null, null)
      }
    },
  },
}

</script>