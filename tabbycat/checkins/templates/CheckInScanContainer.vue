<template>

  <div class="list-group mt-md-2">

    <div class="list-group-item" v-if="!liveScanning">
      <input v-model.string="barcode" autofocus :placeholder="placeholderText"
             type="number" pattern="[0-9]*" inputmode="numeric"
             step="1" class="form-control" :disabled="processing">
    </div>
    <div class="list-group-item pb-3">
      <button v-if="!liveScanning" class="btn btn-block btn-success" @click="toggleScan">
        Scan Using Camera
      </button>
      <button v-if="liveScanning" class="btn btn-block btn-danger" @click="toggleScan">
        Stop Camera Scan
      </button>
      <div id="scanCanvas" v-if="liveScanning"
           class="scan-container ml-auto mt-3 mr-auto">
      </div>
    </div>
    <!-- extra items for error messages -->

  </div>

</template>

<script>
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'

import Quagga from 'quagga'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  data: function() {
    return {
      barcode: "",
      processing: false,
      liveScanning: false,
      scannedResults: [],
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
      document.getElementById('finishedScanSound').play()
      this.barcode = "" // Reset
    },
    finishCheckIn: function(dataResponse, payload, returnPayload) {
      this.processing = false
      var message = dataResponse.time + ' checked-in identifier ' + dataResponse.ids[0]
      $.fn.showAlert("success", message, 0)
    },
    failCheckIn: function(payload, returnPayload) {
      this.processing = false
      var message = 'Failed to check in identifier ' + payload.barcodes[0] + '. Maybe it was misspelt?'
      $.fn.showAlert("danger", message, 0)
    },
    toggleScan: function() {
      this.liveScanning = !this.liveScanning
      // Give time for DOM elements to update
      var self = this
      this.$nextTick(function() {
        if (self.liveScanning) {
          self.streamScan()
        } else {
          Quagga.stop()
        }
      })
    },
    streamScan: function() {
      var self = this

      Quagga.init({
        inputStream : {
          name : "Live",
          type : "LiveStream",
          target: document.querySelector('#scanCanvas')    // Or '#yourElement' (optional)
        },
        decoder : {
          readers : ["code_128_reader"]
        }
      }, function(err) {
        if (err) {
          console.log(err);
          return
        }
        Quagga.start();
      });

      // Draws over frames as they are shown
      Quagga.onProcessed(function(result) {
        var drawingCtx = Quagga.canvas.ctx.overlay,
            drawingCanvas = Quagga.canvas.dom.overlay;

        if (result) {

          if (result.boxes) {
            drawingCtx.clearRect(0, 0, parseInt(drawingCanvas.getAttribute("width")),
                                       parseInt(drawingCanvas.getAttribute("height")));
            result.boxes.filter(function (box) {
                return box !== result.box;
            }).forEach(function (box) {
              // The searching for box
              Quagga.ImageDebug.drawPath(box, {x: 0, y: 1}, drawingCtx,
                                         {color: "#fd681d", lineWidth: 2});
            });
          }

          if (result.box) {
            Quagga.ImageDebug.drawPath(result.box, {x: 0, y: 1}, drawingCtx,
                                       {color: "#663da0", lineWidth: 4});
          }

          if (result.codeResult && result.codeResult.code) {
            Quagga.ImageDebug.drawPath(result.line, {x: 'x', y: 'y'}, drawingCtx,
                                       {color: '#00bf8a', lineWidth: 8});
          }

        }
      })

      // Process a valid result (if it hasn't already been processed
      Quagga.onDetected(function(result) {
        var code = result.codeResult.code;
        // Check length
        if (code.length === 5) {
          // Check numeric
          if (code.match(/^[0-9]+$/) != null) {
            // Check not already posted
            if (!_.includes(self.scannedResults, code)) {
              self.checkInIdentifier(code)
              self.scannedResults.push(code)
            }
          }
        }
      })
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
