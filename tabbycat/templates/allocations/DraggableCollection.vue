<script setup>
import { useDragAndDropStore } from './DragAndDropStore.js'
import { useDraggable } from '../composables/useDraggable.js'

// Passed down from the parent because the trigger for the show/hide needs to be on this element

const props = defineProps({
  locked: {
    type: Boolean,
    default: false,
  },
  dragPayload: Object,
})

const store = useDragAndDropStore()
const { dragStart, dragEnd, draggableClasses } = useDraggable(props)

const dragStartPanel = (event) => {
  store.setPanelDraggingTracker(true)
  dragStart(event)
}

const dragEndPanel = (event) => {
  store.setPanelDraggingTracker(false)
  dragEnd(event)
}
</script>

<template>
  <div
    draggable="true"
    :class="draggableClasses"
    @dragstart="dragStartPanel"
    @dragend="dragEndPanel"
  >
    <slot />
  </div>
</template>
