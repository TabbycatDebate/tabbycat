<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions">
    <div class="thead flex-cell flex-4" data-toggle="tooltip" title="Set the debate's priority (higher importances will be allocated better panels)." slot="himportance">
      <span>Priority</span>
    </div>
    <template slot="hvenue"><!-- Hide Venues --></template>
    <template slot="hpanel">
      <div class="thead flex-cell flex-12 vue-droppable-container">
        <span>Chair</span>
      </div>
      <div class="thead flex-cell flex-12 vue-droppable-container">
        <span>Panel</span>
      </div>
      <div class="thead flex-cell flex-12 vue-droppable-container">
        <span>Trainees</span>
      </div>
    </template>
  </draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">
    <div class="draw-cell flex-4" slot="simportance">
      <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
    </div>
    <template slot="svenue"><!-- Hide Venues --></template>
    <template slot="spanel">
      <div class="draw-cell flex-12 vue-droppable-container">
        <generic-droppable>
          <adjudicator-draggable v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'C')"
            :adjudicator="debateAdjudicator.adjudicator"></adjudicator-draggable>
        </generic-droppable>
      </div>
      <div class="draw-cell flex-12 vue-droppable-container">
        <generic-droppable>
          <adjudicator-draggable v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'P')"
            :adjudicator="debateAdjudicator.adjudicator"></adjudicator-draggable>
        </generic-droppable>
      </div>
      <div class="draw-cell flex-12 vue-droppable-container">
        <generic-droppable>
          <adjudicator-draggable v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'T')"
            :adjudicator="debateAdjudicator.adjudicator"></adjudicator-draggable>
        </generic-droppable>
      </div>
    </template>
  </debate>

  <unallocated-container>
    <div v-for="unallocatedAdj in unallocatedItems">
      <adjudicator-draggable :adjudicator="unallocatedAdj"></venue-draggable>
    </div>
  </unallocated-container>

</div>
</template>

<script>
import DrawContainer from '../mixins/DrawContainer.vue'
import UnallocatedContainer from '../base/UnallocatedContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import DebateImportance from '../draw/DebateImportance.vue'
import DebateAdjudicatorDroppable from '../draganddrops/DebateAdjudicatorDroppable.vue'
import GenericDroppable from '../draganddrops/GenericDroppable.vue'
import AdjudicatorDraggable from '../draganddrops/AdjudicatorDraggable.vue'

import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate, DebateImportance,
    DebateAdjudicatorDroppable, GenericDroppable, AdjudicatorDraggable
  },
  mixins: [
    DrawContainer
  ],
  props: {
  },
  computed: {
  },
  methods: {
    getAdjudicatorsByPosition: function(debate, position) {
      return _.filter(debate.panel, { 'position': position });
    }
  },
  events: {
  }
}

</script>
