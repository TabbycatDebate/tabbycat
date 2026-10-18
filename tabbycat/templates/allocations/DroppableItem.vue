<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'
import { useDragAndDropStore } from './DragAndDropStore.js'


const props = defineProps({
  locked: {
    type: Boolean,
    default: false,
  },
  handleDrop: Function,
  dropContext: Object, // Passed to the handler of the item
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()
const dragCounter = ref(0)
const aboutToDrop = ref(false)

const selected = computed(() => store.isAllocationTargetSelected(props.dropContext))

const selectTarget = (event) => {
  if (event.repeat) return
  if (event.target.closest('a, button, input, select, textarea, [contenteditable="true"], [data-allocation-ignore]')) return
  if (props.locked || store.loading) return
  event.preventDefault()
  event.stopPropagation()
  store.selectAllocationTarget(props.dropContext, props.handleDrop)
  hideHovers()
}

onBeforeUnmount(() => {
  if (selected.value) store.clearAllocationSelection()
})

const hideHovers = () => {
  store.unsetHoverPanel()
  store.unsetHoverConflicts()
}

const dragEnter = () => {
  if (props.locked) {
    return
  }
  dragCounter.value += 1
  aboutToDrop.value = true
}

const dragLeave = () => {
  if (props.locked) {
    return
  }
  dragCounter.value -= 1
  if (dragCounter.value === 0) {
    aboutToDrop.value = false
  }
}

const dragEnd = () => {
  hideHovers()
}

const drop = (event) => {
  dragCounter.value = 0
  if (props.locked) {
    return
  }
  aboutToDrop.value = false
  const dragPayload = JSON.parse(event.dataTransfer.getData('text'))
  store.clearAllocationSelection()
  props.handleDrop(dragPayload, props.dropContext)
  hideHovers()
}

</script>

<template>
  <div
    :class="{ 'vue-droppable-locked': locked, 'vue-droppable-enter': aboutToDrop, 'allocation-selected': selected }"
    class="vue-droppable"
    :tabindex="locked ? -1 : 0"
    role="button"
    :data-allocation-destination="dropContext.assignment !== null"
    :aria-label="dropContext.assignment === null ? gettext('Unallocated items') :
      `${gettext('Allocation destination')} ${dropContext.assignment} ${dropContext.position || ''}`"
    :aria-pressed="selected"
    :aria-disabled="locked || store.loading"
    @click="selectTarget"
    @keydown.enter="selectTarget"
    @keydown.space="selectTarget"
    @dragover.prevent
    @drop.prevent.stop="drop"
    @dragenter="dragEnter"
    @dragleave="dragLeave"
    @dragend="dragEnd"
  >
    <slot />
  </div>
</template>
