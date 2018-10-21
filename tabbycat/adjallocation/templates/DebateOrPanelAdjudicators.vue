<template>

  <div class="d-flex flex-36 vue-droppable vue-droppable-parent p-1"
       :class="{ 'vue-is-drag-enter': isDroppable }">
    <div class="d-flex align-items-center">
      metrics
    </div>
    <draggable-allocation :adjudicators="adjudicators"></draggable-allocation>
  </div>

</template>

<script>
import DraggableAllocation from './DraggableAllocation.vue'

export default {
  components: { DraggableAllocation },
  props: [ 'adjudicators' ],
}
</script>
