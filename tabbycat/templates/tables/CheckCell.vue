<template>

  <td :class="cellData['class'] ? cellData['class'] : null" >

    <span v-if="cellData['sort']" hidden>
      {{ cellData.checked }}
    </span>
    <div class="form-check">
      <input type="checkbox" class="form-check-input  position-static"
             @change="checkUpdate" v-model.boolean.lazy="cellData.checked">
    </div>

  </td>

</template>

<script>
import _ from 'lodash'
import AjaxMixin from '../ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    cellData: Object,
  },
  methods: {
    checkUpdate: function () {
      var cd = this.cellData
      var checked = cd.checked // This is currently the pre-clicked value
      // Updates can be sent off individually via this component itself; or by
      // communicating back up to the Coordinating Vue Container (where they
      // can be handled in bulk or issue via a single bulk method)
      if (_.isUndefined(this.cellData.saveURL)) {
        this.$eventHub.$emit('toggle-checked', cd.id, checked, cd.type)
      } else {
        var message = cd.id + "'s " + cd.type + " status as " + checked
        var payload = { id: cd.id }
        payload[cd.type] = checked
        this.ajaxSave(cd.saveURL, payload, message, null, null, null)
      }
    }
  },
}

</script>