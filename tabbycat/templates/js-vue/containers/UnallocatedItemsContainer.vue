<template>
  <nav
    @dragover.prevent
    @dragenter="dragEnter"
    @dragleave="dragLeave"
    @drop="drop"
    :class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable unallocated-items">

    <slot><!-- Container sets unallocated items here --></slot>

  </nav>
</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  methods: {
    handleDrop: function(event) {
      this.$eventHub.$emit('unassign-draggable', event)
    }
  }
}
</script>