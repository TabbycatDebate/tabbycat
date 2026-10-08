<script setup>
// Note this has to work across the VueX pages (where save updates are located in the store) and
// across checkbox tables (where save updates are notified through callbacks)

import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({ lastSaved: Date })

const { gettext } = useDjangoI18n()

const lastSavedDisplay = ref('')
const animationClass = ref('')
const currentTimer = ref(null)

const paddedMinutes = () => {
  if (!props.lastSaved) {
    return '00'
  }
  const minutes = String(props.lastSaved.getMinutes())
  if (minutes.length === 1) {
    return `0${minutes}`
  }
  return minutes
}

const updatedLastSavedDisplay = () => {
  if (!props.lastSaved) {
    lastSavedDisplay.value = ''
    return
  }
  const secondsLastSaved = Math.abs(new Date() - props.lastSaved) / 1000
  if (secondsLastSaved > 5) {
    animationClass.value = ''
  }
  if (secondsLastSaved > 59) {
    lastSavedDisplay.value = ` at ${props.lastSaved.getHours()}:${paddedMinutes()}`
  } else {
    lastSavedDisplay.value = ` ${parseInt(secondsLastSaved)}s ago`
  }
}

onBeforeUnmount(() => {
  if (currentTimer.value) {
    clearInterval(currentTimer.value)
  }
})

watch(() => props.lastSaved, () => {
  if (currentTimer.value) {
    clearInterval(currentTimer.value)
  }
  updatedLastSavedDisplay()
  animationClass.value = 'save-flash'
  currentTimer.value = setInterval(() => {
    updatedLastSavedDisplay()
  }, 1000)
})
</script>

<template>
  <button
    :class="['btn px-0 border-primary text-primary d-xl-inline vc-auto-save', animationClass]"
    data-toggle="tooltip"
    data-placement="bottom"
    :title="gettext('The time of the last saved change (changes are automatically saved)')"
  >
    <span v-if="lastSavedDisplay === ''">
      <span>{{ gettext('No ') }}</span> <i data-feather="save" />
    </span>
    <span
      v-if="lastSavedDisplay !== ''"
      :class="[animationClass]"
    >{{ lastSavedDisplay }}</span>
  </button>
</template>
