<template>
  <nav
    @dragover.prevent
    @dragenter="dragEnter"
    @dragleave="dragLeave"
    @drop="drop"
    class="navbar navbar-default fixed-bottom p-0"
    :style="{height: height + 'px'}" ref="resizeableElement">

    <section class="resize-handler" @dragover.prevent @mousedown="resizeStart">
      <i data-feather="menu" class="align-self-center mx-auto"></i>
    </section>

    <div class="vue-droppable unallocated-items pt-4 p-2
                justify-content-center d-flex flex-wrap"
         :class="{ 'vue-is-drag-enter': isDroppable }">

      <slot><!-- Container sets unallocated items here --></slot>

    </div>

  </nav>
</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  data: function () {
    return {
      height: null, minHeight: 51, maxHeight: 400, // Defualt to null
      startPosition: null,
    }
  },
  mounted: function () {
    this.height = this.$refs.resizeableElement.clientHeight
  },
  methods: {
    handleDrop: function(event) {
      this.$eventHub.$emit('unassign-draggable', event)
    },
    resizeStart: function(event) {
      event.preventDefault()
      this.startPosition = event.clientY
      window.addEventListener('mousemove', this.resizeMotion);
      window.addEventListener('mouseup', this.resizeEnd);
    },
    resizeMotion: function(event) {
      event.preventDefault()
      var pos = event.clientY
      var moved = (pos - this.startPosition) * 0.03
      var newSize = this.height - moved
      this.height = this.boundedHeight(newSize)
      if (this.height > this.maxHeight) {
        this.resizeEnd(event)
      }
    },
    resizeEnd: function(event) {
      event.preventDefault()
      window.removeEventListener('mousemove', this.resizeMotion);
      window.removeEventListener('mouseup', this.resizeEnd);
    },
    boundedHeight: function(height) {
      if (height > this.maxHeight) {
        return this.maxHeight
      } else if (height < this.minHeight) {
        return this.minHeight
      } else {
        return height
      }
    }
  }
}
</script>
