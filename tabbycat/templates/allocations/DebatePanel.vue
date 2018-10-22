<template>
  <div :class="['draw-cell droppable-cell panel-container flex-horizontal',
                'flex-' + (12 * adjPositions.length)]">

    <div v-for="position in adjPositions" :key="position"
         :class="['legacy-vue-droppable-container', 'position-container-' + position,
                  'positions-limited-' + adjPositions.length]">
      <droppable-generic :assignment-id="debateId"
                         :assignment-position="position"
                         :extra-css="getCSSForPosition(position)"
                         :locked="locked">

        <legacy-draggable-adjudicator
          v-for="da in getAdjudicatorsByPosition(panelAdjudicators, position)"
          :adjudicator="da.adjudicator" :debate-id="debateId"
          :percentiles="percentiles"
          :key="da.adjudicator.id"
          :locked="locked">
        </legacy-draggable-adjudicator>

      </droppable-generic>
    </div>

  </div>
</template>

<script>
import _ from 'lodash'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import LegacyDraggableAdjudicator from '../draganddrops/LegacyDraggableAdjudicator.vue'
import DebateConflictsMixin from '../allocations/DebateConflictsMixin.vue'

export default {
  mixins: [DebateConflictsMixin],
  components: { DroppableGeneric, LegacyDraggableAdjudicator },
  props: ['panelAdjudicators', 'adjPositions', 'panelTeams', 'debateId',
    'percentiles', 'locked', 'roundInfo'],
  computed: {
    adjudicatorIds: function () {
      return _.map(this.panelAdjudicators, da => da.adjudicator.id)
    },
    teamIds: function () {
      return _.map(this.panelTeams, dt => dt.team.id)
    },
  },
  methods: {
    getAdjudicatorsByPosition: function (panelAdjudicators, position) {
      return _.filter(panelAdjudicators, { position: position })
    },
    getCSSForPosition: function (position) {
      let css = 'flex-horizontal '
      const adjs = this.getAdjudicatorsByPosition(this.panelAdjudicators, position).length
      if ((position === 'C' && adjs === 0) || (position === 'P' && adjs % 2 !== 0)) {
        css += 'panel-incomplete'
      }
      return css
    },
  },
}
</script>
