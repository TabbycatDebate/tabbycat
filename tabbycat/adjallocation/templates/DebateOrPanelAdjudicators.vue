<template>

  <div class="d-flex flex-36 flex-truncate vue-droppable vue-droppable-parent">
    <div class="d-flex align-items-center small">
      metrics
    </div>
    <draggable-allocation :handle-debate-or-panel-drop="handleDebateOrPanelDrop"
                          :debate-or-panel="debateOrPanel"></draggable-allocation>
  </div>

</template>

<script>
import DraggableAllocation from './DraggableAllocation.vue'

export default {
  components: { DraggableAllocation },
  props: [ 'debateOrPanel', 'handleDebateOrPanelDrop' ],
}
</script>
