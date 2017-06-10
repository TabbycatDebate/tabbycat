<template>
  <div class="vue-droppable"
       @dragover.prevent
       @drop="drop"
       @dragenter="dragEnter"
       @dragleave="dragLeave"
       :class="{ 'vue-is-drag-enter': isDroppable }">

    <slot><!-- Container sets the dropped items here --></slot>

  </div>
</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: { droppable: Object, assignmentId: Number, assignmentPosition: String },
  methods: {
    handleDrop: function(event) {
      this.$eventHub.$emit('assign-draggable', event, this.assignmentId, this.assignmentPosition)
    }
  }
}
</script>
