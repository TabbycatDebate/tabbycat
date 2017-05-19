<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate">

    <importance>
      <debate-importance
        :id="debate.id"
        :importance="debate.importance">
        <!-- :url="this.roundInfo['updateImportanceURL']" -->
      </debate-importance>
    </importance>

    <panel>
      TODO
<!--       <debate-adjudicator-droppable
          :adjudicators="debateAdjudicators.chair"
          :debate-id="debate.id" :position="'C'"
          v-on:propogateSetAdj="propogateSetAdj"
          v-on:propogateUnsetAdj="propogateUnsetAdj">
      </debate-adjudicator-droppable>
      <debate-adjudicator-droppable
          :adjudicators="debateAdjudicators.panelists"
          :debate-id="debate.id" :position="'P'"
          v-on:propogateSetAdj="propogateSetAdj"
          v-on:propogateUnsetAdj="propogateUnsetAdj">
      </debate-adjudicator-droppable>
      <debate-adjudicator-droppable
          :adjudicators="debateAdjudicators.trainees"
          :debate-id="debate.id" :position="'T'"
          v-on:propogateSetAdj="propogateSetAdj"
          v-on:propogateUnsetAdj="propogateUnsetAdj">
      </debate-adjudicator-droppable> -->
    </panel>

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
// import DebateAdjudicatorDroppable from '../draganddrops/DebateAdjudicatorDroppable.vue'
import AdjudicatorDraggable from '../draganddrops/AdjudicatorDraggable.vue'

import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate,
    AdjudicatorDraggable
  },
  mixins: [
    DrawContainer
  ],
  props: {
  },
  computed: {
  },
  methods: {
  },
  events: {
  }
}

</script>
