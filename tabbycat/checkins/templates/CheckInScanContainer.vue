<script setup>
import _ from 'lodash'
import Quagga from 'quagga'

import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useWebSocket } from '../../templates/composables/useWebSocket.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  tournamentSlug: String,
})

const { gettext, tct } = useDjangoI18n()

const entry = ref(null)
const barcode = ref('')
const liveScanning = ref(false)
const scannedResults = ref([])
const sentIdentifiers = ref([])
const sound = ref(false)

const sockets = ['checkins']
const tournamentSlugForWSPath = computed(() => props.tournamentSlug)

const playSound = (elementID) => {
  const promise = document.getElementById(elementID).play()
  if (promise !== undefined) {
    promise.catch(() => {
      console.debug('Safari autoplay ... needs permission for sound')
    })
  }
}

const finishCheckIn = (payload) => {
  const checkin = payload.checkins[0]
  const substitutions = [checkin.time, checkin.identifier, checkin.owner_name]
  const msg = tct('<span class="text-monospace">%s checked in %s:</span> %s', substitutions)
  window.$?.fn?.showAlert?.('success', msg, 0)
  playSound('finishedScanSound')
}

const failCheckIn = (error, message) => {
  if (error) {
    console.error(error)
  }
  window.$?.fn?.showAlert?.('danger', message, 0)
  playSound('failedScanSound')
}

const handleSocketReceive = (_socketLabel, payload) => {
  // Only respond to IDs that have been sent by this form
  if (payload.component_id !== componentId) {
    return
  }
  finishCheckIn(payload)
}

const handleSocketError = (_socketLabel, payload) => {
  // Only respond to IDs that have been sent by this form
  if (payload.component_id !== componentId) {
    return
  }
  failCheckIn(payload.error, payload.message)
}

const { sendToSocket, componentId } = useWebSocket({
  sockets,
  tournamentSlugForWSPath,
  handleSocketReceive,
  handleSocketError,
})

const checkInIdentifier = async (barcodeIdentifier) => {
  const payload = { barcodes: [barcodeIdentifier], status: true, type: 'people' }
  sentIdentifiers.value.push(barcodeIdentifier)
  sendToSocket('checkins', payload)
  barcode.value = ''
  if (!liveScanning.value) {
    await nextTick()
    entry.value?.focus?.()
  }
}

const unMute = () => {
  document.getElementById('finishedScanSound').muted = false
  document.getElementById('failedScanSound').muted = false
  sound.value = true
}

const streamScan = () => {
  Quagga.init({
    inputStream: {
      name: 'Live',
      type: 'LiveStream',
      target: document.querySelector('#scanCanvas'),
    },
    decoder: {
      readers: ['code_128_reader'],
    },
  }, (err) => {
    if (err) {
      console.debug('Initialization failed due to user camera permissions denial.')
      liveScanning.value = false
      return
    }
    Quagga.start()
  })

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

  Quagga.onDetected((result) => {
    const code = result.codeResult.code
    if (code.length === 6) {
      if (code.match(/^[0-9]+$/) !== null) {
        if (!_.includes(scannedResults.value, code)) {
          checkInIdentifier(code)
          scannedResults.value.push(code)
        } else {
          // noop
        }
      }
    }
  })
}

const toggleScan = async () => {
  liveScanning.value = !liveScanning.value
  await nextTick()
  if (liveScanning.value) {
    streamScan()
    document.getElementById('pageTitle').style.display = 'none'
  } else {
    Quagga.stop()
    document.getElementById('pageTitle').style.display = 'block'
  }
}

watch(() => barcode.value, (current) => {
  if (String(current).length >= 6) {
    checkInIdentifier(current)
  }
})

onBeforeUnmount(() => {
  try {
    Quagga.stop()
  } catch (e) {
    // noop
  }
})
</script>

<template>
  <div class="list-group mt-3">
    <div
      v-if="!liveScanning"
      class="list-group-item"
    >
      <input
        ref="entry"
        v-model="barcode"
        type="number"
        pattern="[0-9]*"
        autofocus
        inputmode="numeric"
        step="1"
        class="form-control"
      >
    </div>
    <div class="list-group-item pb-3">
      <div class="d-flex">
        <div class="flex-fill pr-2">
          <button
            v-if="!liveScanning"
            class="btn btn-block btn-success"
            @click="toggleScan"
          >
            {{ gettext('Scan Using Camera') }}
          </button>
          <button
            v-if="liveScanning"
            class="btn btn-block btn-danger"
            @click="toggleScan"
          >
            {{ gettext('Stop Camera Scan') }}
          </button>
        </div>
        <div
          v-if="!sound"
          class="flex-fill pl-2"
        >
          <button
            class="btn btn-block btn-success"
            @click="unMute"
          >
            {{ gettext('Turn On Sounds') }}
          </button>
        </div>
      </div>
      <div
        v-if="liveScanning"
        id="scanCanvas"
        class="scan-container ml-auto mt-3 mr-auto"
      />
    </div>
    <!-- extra items for error messages -->
  </div>
</template>
