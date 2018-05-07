<template>

  <div class="list-group mt-3">

    <div class="list-group-item" v-if="!liveScanning">
      <input v-model="barcode" :placeholder="placeholderText"
             type="number" pattern="[0-9]*" inputmode="numeric" step="1"
             class="form-control" ref="entry" autofocus>
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
import _ from 'lodash'
import Quagga from 'quagga'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  data: function () {
    return {
      barcode: '',
      liveScanning: false,
      scannedResults: [],
    }
  },
  props: {
    scanUrl: String,
  },
  methods: {
    checkInIdentifier: function (barcodeIdentifier) {
      var message = `the checkin status of ${barcodeIdentifier}`
      var payload = { barcodes: [barcodeIdentifier], status: true }
      this.ajaxSave(
        this.scanUrl, payload, message, this.finishCheckIn, this.failCheckIn,
        null, false,
      )
      // Audio Problem
      var promise = document.getElementById('finishedScanSound').play()
      if (promise !== undefined) {
        promise.catch(error => {
          // Auto-play was prevented
          // Show a UI element to let the user manually start playback
          console.log('Safari autoplay ... needs permission for sound')
        })
      }
      this.barcode = '' // Reset
      if (!this.liveScanning) {
        this.$nextTick(() => this.$refs.entry.focus()) // Set focus back to input
      }
    },
    finishCheckIn: function (dataResponse, payload, returnPayload) {
      var message = dataResponse.time + ' checked-in identifier ' + dataResponse.ids[0]
      $.fn.showAlert("success", message, 0)
    },
    failCheckIn: function (payload, returnPayload) {
      var message = 'Failed to check in identifier ' + payload.barcodes[0] + '. Maybe it was misspelt?'
      $.fn.showAlert("danger", message, 0)
    },
    toggleScan: function () {
      this.liveScanning = !this.liveScanning
      // Give time for DOM elements to update
      var self = this
      this.$nextTick(function () {
        if (self.liveScanning) {
          self.streamScan()
          document.getElementById("pageTitle").style.display = 'none'
        } else {
          Quagga.stop()
          document.getElementById("pageTitle").style.display = 'block'
        }
      })
    },
    streamScan: function () {
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
      }, function (err) {
        if(err) {
          console.log("Initialization failed due to user camera permissions denial.");
          self.liveScanning = false
          return
        }
        Quagga.start();
      });

      // Draws over frames as they are shown
      Quagga.onProcessed(function (result) {
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
      Quagga.onDetected(function (result) {
        var code = result.codeResult.code;
        // Check length
        if (code.length === 5) {
          // Check numeric
          if (code.match(/^[0-9]+$/) != null) {
            // Check not already posted
            if (!_.includes(self.scannedResults, code)) {
              self.checkInIdentifier(code)
              self.scannedResults.push(code)
            } else {
              // $.fn.showAlert("info", 'Already checked-in identifier ' + code, 0)
            }
          }
        }
      })
    },
  },
  watch: {
    barcode: function (current, old) {
      if (current.length >= 5) {
        this.processing = true
        this.checkInIdentifier(current)
      }
    }
  }
}
</script>
