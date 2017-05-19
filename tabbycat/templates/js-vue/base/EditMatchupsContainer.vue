<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate">

    <template v-for="(team, index) in debate.teams">
      <team-draggable :team="team" :slot="index"> </team-draggable>
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
import TeamDraggable from '../draganddrops/TeamDraggable.vue'
import _ from 'lodash'


export default {
  components: {
    DrawHeader, UnallocatedContainer, Debate, TeamDraggable
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
