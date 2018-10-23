<template>

  <div class="d-flex flex-fill align-items-stretch align-items-center
                         vue-draggable-child">
    <div class="p-2 d-flex align-items-center">
      <i data-feather="move"></i>
    </div>
    <div class="flex-1 d-flex border-left">
      <droppable-item class="flex-grow-1 p-1" @handledrop="handledrop">
        <draggable-adjudicator v-if="chairID" class="flex-fill" :item="allAdjudicators[chairID]"
                               :drop-payload="getDropPayload(chairID, 'C')">
        </draggable-adjudicator>
      </droppable-item>
    </div>
    <div class="flex-3 d-flex flex-wrap border-left">
      <droppable-item class="flex-grow-1 p-1" @handledrop="handledrop">
        <draggable-adjudicator v-for="adjID in adjudicators.P" :item="allAdjudicators[adjID]"
                               :drop-payload="getDropPayload(adjID, 'P')" :key="adjID">
        </draggable-adjudicator>
      </droppable-item>
    </div>
    <div class="flex-1 d-flex border-left">
      <droppable-item class="flex-grow-1 p-1" @handledrop="handledrop">
        <draggable-adjudicator v-for="adjID in adjudicators.T" :item="allAdjudicators[adjID]"
                               :drop-payload="getDropPayload(adjID, 'T')" :key="adjID">
        </draggable-adjudicator>
      </droppable-item>
    </div>
  </div>

</template>

<script>
import DroppableItem from '../../utils/templates/DroppableItem.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'

export default {
  components: { DraggableAdjudicator, DroppableItem },
  props: [ 'debateOrPanel' ],
  computed: {
    chairID () {
      return this.adjudicators.C[0]
    },
    allAdjudicators () {
      return this.$store.getters.allocatableItems
    },
    adjudicators () {
      return this.debateOrPanel.adjudicators
    },
  },
  methods: {
    getDropPayload: function (adjID, position) {
      return {
        'item': adjID,
        'assignment': this.debateOrPanel.id,
        'position': position,
      }
    },
    handledrop: function (droppedData) {
      console.log('handledrop', droppedData)
      // Emit the 'send adj to this debate method'
    },
  },
}
</script>
