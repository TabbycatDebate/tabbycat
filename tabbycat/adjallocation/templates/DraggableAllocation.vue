<template>

  <div>
    <div>
      <draggable-adjudicator v-if="adjudicators.C[0]"
                             :item="allAdjudicators[adjudicators.C[0]]">
      </draggable-adjudicator>
    </div>
    <div>
      <draggable-adjudicator v-for="adjID in adjudicators.P"
                             :item="allAdjudicators[adjID]" :key="adjID">
      </draggable-adjudicator>
    </div>
    <div>
      <draggable-adjudicator v-for="adjID in adjudicators.T"
                             :item="allAdjudicators[adjID]" :key="adjID">
      </draggable-adjudicator>
    </div>
  </div>

</template>

<script>
import DraggableAdjudicator from './DraggableAdjudicator.vue'

export default {
  components: { DraggableAdjudicator },
  props: [ 'adjudicators' ],
  computed: {
    allAdjudicators () {
      return this.$store.getters.allocatableItems
    },
  },
}
</script>
