<template>
  <div :class="[droppableClasses, extraCss]"
       @dragover.prevent @drop="drop"
       @dragenter="dragEnter" @dragleave="dragLeave">

    <div v-if="locked" class="vue-droppable-lock-spinner">
      <i data-feather="loader" class="spinning"></i>
    </div>
    <slot><!-- Container sets the dropped items here --></slot>

  </div>
</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: { assignmentId: Number, assignmentPosition: String, extraCss: "" },
  methods: {
    handleDrop: function(event) {
      this.$eventHub.$emit('assign-draggable', event, this.assignmentId, this.assignmentPosition)
    }
  }
}
</script>
