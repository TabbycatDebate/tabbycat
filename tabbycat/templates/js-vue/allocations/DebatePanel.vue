<template>
  <div :class="['draw-cell droppable-cell panel-container flex-horizontal',
                'flex-' + (12 * adjPositions.length)]">

    <div v-for="position in adjPositions"
         :class="['vue-droppable-container', 'position-container-' + position,
                  'positions-limited-' + adjPositions.length]">
      <droppable-generic :assignment-id="debateId"
                         :assignment-position="position"
                         :extra-css="getCSSForPosition(position)"
                         :locked="locked">

        <draggable-adjudicator
          v-for="da in getAdjudicatorsByPosition(panelAdjudicators, position)"
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
import DebateConflictsMixin from '../allocations/DebateConflictsMixin.vue'
import _ from 'lodash'

export default {
  mixins: [DebateConflictsMixin],
  components: { DroppableGeneric, DraggableAdjudicator },
  props: ['panelAdjudicators', 'adjPositions', 'panelTeams', 'debateId',
          'percentiles', 'locked', ],
  methods: {
    getAdjudicatorsByPosition: function(panelAdjudicators, position) {
      return _.filter(panelAdjudicators, { 'position': position })
    },
    getCSSForPosition: function(position) {
      var css = 'flex-horizontal '
      var adjs = this.getAdjudicatorsByPosition(this.panelAdjudicators, position).length
      if ((position === "C" && adjs === 0) ||
          (position === "P" && adjs % 2 != 0)) {
        return css += 'panel-incomplete'
      }
      return css
    }
  },
}
</script>