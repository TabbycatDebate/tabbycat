<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">

    <template v-for="(team, index) in debate.teams">
      <generic-droppable :slot="'sposition' + index">
        <team-draggable :team="team"></team-draggable>
      </generic-droppable>
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
import _ from 'lodash'


export default {
  components: {
    DrawHeader, UnallocatedContainer, Debate, GenericDroppable, TeamDraggable
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
