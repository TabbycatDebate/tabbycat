<template>

  <div @dragover.prevent @drop.prevent.stop="drop"
       :class="{ 'vue-droppable-locked': locked, 'vue-droppable-enter': aboutToDrop }"
       @dragenter="dragEnter" @dragleave="dragLeave" @dragend="dragEnd"
       class="vue-droppable">

    <slot></slot>

  </div>

</template>

<script>
import { mapMutations } from 'vuex'

export default {
  props: {
    locked: {
      type: Boolean,
      default: false,
    },
    handleDrop: Function,
    dropContext: Object, // Passed to the handler of the item
  },
  data: function () {
    return {
      dragCounter: 0,
      aboutToDrop: false,
    }
  },
  methods: {
    hideHovers: function () {
      this.unsetHoverPanel()
      this.unsetHoverConflicts()
    },
    dragEnter: function (event) {
      if (this.locked) {
        return // Don't allow
      }
      this.dragCounter += 1
      this.aboutToDrop = true
    },
    dragLeave: function (event) {
      if (this.locked) {
        return // Don't allow
      }
      this.dragCounter -= 1
      if (this.dragCounter === 0) {
        this.aboutToDrop = false
      }
    },
    dragEnd: function () {
      // When dropped there is no event fired that would normally dismiss hover panels or conflicts
      this.hideHovers()
    },
    drop: function (event) {
      this.dragCounter = 0
      if (this.locked) {
        return // Don't allow
      }
      this.aboutToDrop = false
      // Send data to parent's handler method (after de-serialising it)
      const dragPayload = JSON.parse(event.dataTransfer.getData('text'))
      this.handleDrop(dragPayload, this.dropContext) // Call page-specific method handler passed down
      this.hideHovers()
    },
    ...mapMutations(['unsetHoverPanel', 'unsetHoverConflicts']),
  },
}
</script>
