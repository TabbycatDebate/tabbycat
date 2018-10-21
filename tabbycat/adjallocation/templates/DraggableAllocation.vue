<template>

  <draggable-item class="d-flex flex-fill align-items-stretch align-items-center
                         vue-draggable-child">
    <div class="p-2 d-flex align-items-center">
      <i data-feather="move"></i>
    </div>
    <div class="flex-1 p-1 d-flex border-left vue-droppable"
        :class="{ 'vue-is-drag-enter': isDroppable }">
      <draggable-adjudicator v-if="adjudicators.C[0]" class="flex-fill"
                             :item="allAdjudicators[adjudicators.C[0]]">
      </draggable-adjudicator>
    </div>
    <div class="flex-3 p-1 d-flex flex-wrap border-left vue-droppable"
        :class="{ 'vue-is-drag-enter': isDroppable }">
      <draggable-adjudicator v-for="adjID in adjudicators.P"
                             :item="allAdjudicators[adjID]" :key="adjID">
      </draggable-adjudicator>
    </div>
    <div class="flex-1 p-1 d-flex border-left vue-droppable"
        :class="{ 'vue-is-drag-enter': isDroppable }">
      <draggable-adjudicator v-for="adjID in adjudicators.T"
                             :item="allAdjudicators[adjID]" :key="adjID">
      </draggable-adjudicator>
    </div>
  </draggable-item>

</template>

<script>
import DraggableItem from '../../utils/templates/DraggableItem.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'

export default {
  components: { DraggableAdjudicator, DraggableItem },
  props: [ 'adjudicators' ],
  computed: {
    allAdjudicators () {
      return this.$store.getters.allocatableItems
    },
  },
}
</script>
