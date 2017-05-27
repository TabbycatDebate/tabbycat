<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">

    <debate-importance slot="simportance"
      :id="debate.id" :importance="debate.importance"></debate-importance>

    <div slot="spanel">
      <debate-adjudicator-droppable :position="'C'"
        :position-adjudicators="getAdjudicatorsByPosition(debate, 'C')"></debate-adjudicator-droppable>
      <debate-adjudicator-droppable :position="'P'"
        :position-adjudicators="getAdjudicatorsByPosition(debate, 'P')"></debate-adjudicator-droppable>
      <debate-adjudicator-droppable :position="'T'"
        :position-adjudicators="getAdjudicatorsByPosition(debate, 'T')"></debate-adjudicator-droppable>
    </div>

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
import AdjudicatorDraggable from '../draganddrops/AdjudicatorDraggable.vue'

import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate, DebateImportance,
    DebateAdjudicatorDroppable, AdjudicatorDraggable
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
