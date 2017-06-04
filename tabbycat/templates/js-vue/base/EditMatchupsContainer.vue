<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <team-slideover :team="slideSubject"></team-slideover>

  <draw-header :positions="positions">
    <template slot="hteams">
      <div class="thead flex-cell flex-8 vue-droppable-container" data-toggle="tooltip" title="test"
        v-for="position in positions">
        <span>{{ position }}</span>
      </div>
    </template>
  </draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">
    <template v-for="(team, index) in debate.teams">
      <div class="draw-cell flex-8 vue-droppable-container" :slot="'sposition' + index">
        <generic-droppable>
          <team-draggable :team="team"></team-draggable>
        </generic-droppable>
      </div>
    </template>
  </debate>

  <unallocated-container>
    <div v-for="unallocatedTeam in unallocatedItems">
      <team-draggable :team="unallocatedTeam"> </team-draggable>
    </div>
  </unallocated-container>

</div>
</template>

<script>
import DrawContainer from '../mixins/DrawContainer.vue'
import UnallocatedContainer from '../base/UnallocatedContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import GenericDroppable from '../draganddrops/GenericDroppable.vue'
import TeamDraggable from '../draganddrops/TeamDraggable.vue'
import TeamSlideover from '../slideovers/TeamSlideover.vue'
import _ from 'lodash'


export default {
  mixins: [
    DrawContainer
  ],
  components: {
    DrawHeader, UnallocatedContainer, Debate, GenericDroppable, TeamDraggable, TeamSlideover
  },
  props: {
  },
  computed: {
  },
  methods: {
  },
}

</script>
