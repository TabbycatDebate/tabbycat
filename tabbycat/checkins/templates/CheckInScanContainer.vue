<template>

  <div class="list-group mt-3">

    <div class="list-group-item">
      <input v-model.string="barcode" autofocus placeholder="identifier"
             type="number" step="1" class="form-control">
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
    }
  },
  components: { },
  props: { },
  computed: { },
  methods: {
    checkInIdentifier: function(barcodeIdentifier) {
      var payload = {
        'barcode': barcodeIdentifier
      }
      this.ajaxSave(this.checkInURL, barcodeIdentifier, 'test',
                    this.finishCheckIn(), this.failCheckIn(), null)
      this.barcode = "" // Reset
    },
    finishCheckIn: function() {
      console.log('fininished')
    },
    failCheckIn: function() {
      console.log('failed')
    }
  },
  watch: {
    barcode: function(current, old) {
      if (current.length >= 5) {
        this.checkInIdentifier(current.toInteger())
      }
    }
  }
}
</script>
