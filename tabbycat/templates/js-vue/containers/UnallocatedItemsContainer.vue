<template>
  <nav
    @dragover.prevent
    @dragenter="dragEnter"
    @dragleave="dragLeave"
    @drop="drop"
    :class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable unallocated-items"
    :style="{height: height + 'px'}" ref="resizeableElement">

    <slot><!-- Container sets unallocated items here --></slot>

    <div class="resize-handler navbar-toggle collapsed"
         @dragover.prevent @mousedown="resizeStart">
      <span class="glyphicon glyphicon-menu-hamburger"></span>
    </div>

  </nav>
</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  data: function () {
    return {
      height: null, minHeight: 60, maxHeight: 400, // Defualt to null
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
      var moved = (pos - this.startPosition)
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
