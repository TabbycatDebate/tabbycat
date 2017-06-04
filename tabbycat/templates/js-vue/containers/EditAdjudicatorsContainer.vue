<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <!-- <team-slideover :team="slideSubject"></team-slideover> -->

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
        <droppable-generic>
          <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'C')"
            :adjudicator="debateAdjudicator.adjudicator"></draggable-adjudicator>
        </droppable-generic>
      </div>
      <div class="draw-cell flex-12 vue-droppable-container">
        <droppable-generic>
          <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'P')"
            :adjudicator="debateAdjudicator.adjudicator"></draggable-adjudicator>
        </droppable-generic>
      </div>
      <div class="draw-cell flex-12 vue-droppable-container">
        <droppable-generic>
          <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'T')"
            :adjudicator="debateAdjudicator.adjudicator"></draggable-adjudicator>
        </droppable-generic>
      </div>
    </template>
  </debate>

  <unallocated-items-container>
    <div v-for="unallocatedAdj in unallocatedItems">
      <draggable-adjudicator :adjudicator="unallocatedAdj"></draggable-adjudicator>
    </div>
  </unallocated-items-container>

</div>
</template>

<script>
import DrawContainer from '../containers/DrawContainer.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import DebateImportance from '../draw/DebateImportance.vue'
// import DebateAdjudicatorDroppable from '../draganddrops/DebateAdjudicatorDroppable.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'

import _ from 'lodash'


export default {
  components: {
    UnallocatedItemsContainer, DrawHeader, Debate, DebateImportance,
    // DebateAdjudicatorDroppable,
    DroppableGeneric, DraggableAdjudicator
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
