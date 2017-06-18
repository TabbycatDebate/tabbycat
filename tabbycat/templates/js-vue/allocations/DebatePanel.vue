<template>
  <div class="draw-cell panel-container flex-36 flex-horizontal">

    <div v-for="position in adjPositions"
         :class="['vue-droppable-container', 'position-container-' + position]">
      <droppable-generic :assignment-id="debateId"
                         :assignment-position="position"
                         :extra-css="'flex-horizontal'"
                         :locked="locked">

        <draggable-adjudicator
          v-for="da in getAdjudicatorsByPosition(panel, position)"
          :adjudicator="da.adjudicator" :debate-id="debateId"
          :percentiles="percentiles" :key="da.adjudicator.id"
          :locked="locked">
        </draggable-adjudicator>

      </droppable-generic>
    </div>

  </div>
</template>

<script>
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'
import _ from 'lodash'

export default {
  mixins: [],
  components: { DroppableGeneric, DraggableAdjudicator },
  data: function () {
    return {
      adjPositions: ["C", "P", "T"] // Used to iterate in templates
    }
  },
  props: ['panel', 'debateId', 'percentiles', 'locked'],
  methods: {
    getAdjudicatorsByPosition: function(panel, position) {
      return _.filter(panel, { 'position': position })
    },
  },
}
</script>