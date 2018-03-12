<template>

  <div class="list-group mt-3">

    <div class="list-group-item">
      <input v-model.string="barcode" autofocus :placeholder="placeholderText"
             type="number" step="1" class="form-control" :disabled="processing">
    </div>
    <!-- extra items for error messages -->

  </div>

</template>

<script>
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'

import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  data: function() {
    return {
      barcode: "",
      processing: false
    }
  },
  props: {
    'scanUrl': String
  },
  computed: {
    placeholderText: function() {
      if (this.processing === true) {
        return "processing scan..."
      } else {
        return "enter barcode identifier"
      }
    }
  },
  methods: {
    checkInIdentifier: function(barcodeIdentifier) {
      var message = 'the checkin status of ' + barcodeIdentifier
      var payload = { 'barcodes': [barcodeIdentifier] }
      this.ajaxSave(this.scanUrl, payload, message,
                    this.finishCheckIn, this.failCheckIn, null, false)
      this.barcode = "" // Reset
    },
    finishCheckIn: function(dataResponse, payload, returnPayload) {
      this.processing = false
      var message = dataResponse.time + ' checked-in identifier ' + dataResponse.ids[0]
      $.fn.showAlert("success", message, 0)
    },
    failCheckIn: function(payload, returnPayload) {
      this.processing = false
      var message = 'Failed to check in identifier ' + payload.barcodes[0] + ' maybe it was misspelt?'
      $.fn.showAlert("danger", message, 0)
    }
  },
  watch: {
    barcode: function(current, old) {
      if (current.length >= 5) {
        this.processing = true
        this.checkInIdentifier(current)
      }
    }
  }
}
</script>
