<template>

  <div class="d-flex">
    <div class="p-2 flex-grow-1">
      <draggable-allocation :adjudicators="adjudicators"></draggable-allocation>
    </div>
    <div class="p-2 flex-grow-1">
      panel metrics here
    </div>
  </div>

</template>

<script>
import DraggableAllocation from './DraggableAllocation.vue'

export default {
  components: { DraggableAllocation },
  props: [ 'adjudicators' ],
}
</script>
