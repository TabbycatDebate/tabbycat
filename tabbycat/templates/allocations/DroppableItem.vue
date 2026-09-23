<script setup>
import { ref } from 'vue'
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
const dragCounter = ref(0)
const aboutToDrop = ref(false)

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
  props.handleDrop(dragPayload, props.dropContext)
  hideHovers()
}

</script>

<template>
  <div
    :class="{ 'vue-droppable-locked': locked, 'vue-droppable-enter': aboutToDrop }"
    class="vue-droppable"
    @dragover.prevent
    @drop.prevent.stop="drop"
    @dragenter="dragEnter"
    @dragleave="dragLeave"
    @dragend="dragEnd"
  >
    <slot />
  </div>
</template>
