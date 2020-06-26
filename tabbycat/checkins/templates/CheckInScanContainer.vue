<template>

  <div class="list-group mt-3">

    <div class="list-group-item" v-if="!liveScanning">
      <input v-model="barcode" type="number" pattern="[0-9]*" autofocus
             inputmode="numeric" step="1" class="form-control" ref="entry" >
    </div>
    <div class="list-group-item pb-3">
      <div class="d-flex">
        <div class="flex-fill pr-2">
          <button v-if="!liveScanning" v-text="gettext('Scan Using Camera')" class="btn btn-block btn-success" @click="toggleScan"></button>
          <button v-if="liveScanning" v-text="gettext('Stop Camera Scan')" class="btn btn-block btn-danger" @click="toggleScan"></button>
        </div>
        <div v-if="!sound" class="flex-fill pl-2">
          <button v-text="gettext('Turn On Sounds')" class="btn btn-block btn-success" @click="unMute"></button>
        </div>
      </div>
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

import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'

export default {
  mixins: [WebSocketMixin],
  data: function () {
    return {
      barcode: '',
      liveScanning: false,
      scannedResults: [],
      sentIdentifiers: [],
      sound: false,
      sockets: ['checkins'],
    }
  },
  props: {
    tournamentSlug: String,
  },
  computed: {
    tournamentSlugForWSPath: function () {
      return this.tournamentSlug
    },
  },
  methods: {
    checkInIdentifier: function (barcodeIdentifier) {
      const payload = { barcodes: [barcodeIdentifier], status: true, type: 'people' }
      this.sentIdentifiers.push(barcodeIdentifier) // Note what has been sent
      this.sendToSocket('checkins', payload)
      this.barcode = '' // Reset
      if (!this.liveScanning) {
        this.$nextTick(() => this.$refs.entry.focus()) // Set focus back to input
      }
    },
    receiveFromSocket: function (socketLabel, payload) {
      // Note overriding WebSocketMixin here to use sounds/inline alerts
      // Note only responding to IDs that have been sent by this form —
      // don't want to show checkins from everywhere else
      if (payload.component_id !== this.componentId) {
        return // Didn't come from this form
      }
      if (Object.prototype.hasOwnProperty.call(payload, 'error')) {
        this.failCheckIn(payload.error, payload.message, null)
      } else {
        this.finishCheckIn(payload)
      }
    },
    finishCheckIn: function (payload) {
      const checkin = payload.checkins[0]
      const substitutions = [checkin.time, checkin.identifier, checkin.owner_name]
      const msg = this.tct('<span class="text-monospace">%s checked in %s:</span> %s', substitutions)
      $.fn.showAlert('success', msg, 0)
      this.playSound('finishedScanSound')
    },
    failCheckIn: function (error, message) {
      if (error) {
        console.error(error)
      }
      $.fn.showAlert('danger', message, 0)
      this.playSound('failedScanSound')
    },
    unMute: function () {
      document.getElementById('finishedScanSound').muted = false
      document.getElementById('failedScanSound').muted = false
      this.sound = true
    },
    playSound: function (elementID) {
      // Audio Problem
      const promise = document.getElementById(elementID).play()
      if (promise !== undefined) {
        promise.catch(() => {
          // Auto-play was prevented
          // Show a UI element to let the user manually start playback
          console.debug('Safari autoplay ... needs permission for sound')
        })
      }
    },
    toggleScan: function () {
      this.liveScanning = !this.liveScanning
      // Give time for DOM elements to update
      const self = this
      this.$nextTick(() => {
        if (self.liveScanning) {
          self.streamScan()
          document.getElementById('pageTitle').style.display = 'none'
        } else {
          Quagga.stop()
          document.getElementById('pageTitle').style.display = 'block'
        }
      })
    },
    streamScan: function () {
      const self = this

      Quagga.init({
        inputStream: {
          name: 'Live',
          type: 'LiveStream',
          target: document.querySelector('#scanCanvas'), // Or '#yourElement' (optional)
        },
        decoder: {
          readers: ['code_128_reader'],
        },
      }, (err) => {
        if (err) {
          console.debug('Initialization failed due to user camera permissions denial.')
          self.liveScanning = false
          return
        }
        Quagga.start()
      })

      // Draws over frames as they are shown
      Quagga.onProcessed((result) => {
        const drawingCtx = Quagga.canvas.ctx.overlay
        const drawingCanvas = Quagga.canvas.dom.overlay

        if (result) {
          if (result.boxes) {
            drawingCtx.clearRect(
              0, 0,
              parseInt(drawingCanvas.getAttribute('width')),
              parseInt(drawingCanvas.getAttribute('height')),
            )
            result.boxes.filter(box => box !== result.box).forEach((box) => {
              // The searching for box
              Quagga.ImageDebug.drawPath(
                box, { x: 0, y: 1 }, drawingCtx,
                { color: '#fd681d', lineWidth: 2 },
              )
            })
          }
          if (result.box) {
            Quagga.ImageDebug.drawPath(
              result.box, { x: 0, y: 1 }, drawingCtx,
              { color: '#663da0', lineWidth: 4 },
            )
          }
          if (result.codeResult && result.codeResult.code) {
            Quagga.ImageDebug.drawPath(
              result.line, { x: 'x', y: 'y' }, drawingCtx,
              { color: '#00bf8a', lineWidth: 8 },
            )
          }
        }
      })
      // Process a valid result (if it hasn't already been processed
      Quagga.onDetected((result) => {
        const code = result.codeResult.code
        // Check length
        if (code.length === 6) {
          // Check numeric
          if (code.match(/^[0-9]+$/) !== null) {
            // Check not already posted
            if (!_.includes(self.scannedResults, code)) {
              self.checkInIdentifier(code)
              self.scannedResults.push(code)
            } else {
              // $.fn.showAlert("info", 'Already checked in identifier ' + code, 0)
            }
          }
        }
      })
    },
  },
  watch: {
    barcode: function (current) {
      if (current.length >= 6) {
        this.processing = true
        this.checkInIdentifier(current)
      }
    },
  },
}
</script>
