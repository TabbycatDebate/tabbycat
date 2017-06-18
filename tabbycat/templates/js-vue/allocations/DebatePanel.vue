<template>
  <div :class="['draw-cell panel-container flex-horizontal',
                'flex-' + (12 * adjPositions.length)]">

    <div v-for="position in adjPositions"
         :class="['vue-droppable-container', 'position-container-' + position,
                  'positions-limited-' + adjPositions.length]">
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
  props: ['panel', 'debateId', 'percentiles', 'locked', 'adjPositions'],
  methods: {
    getAdjudicatorsByPosition: function(panel, position) {
      return _.filter(panel, { 'position': position })
    },
  },
}
</script>