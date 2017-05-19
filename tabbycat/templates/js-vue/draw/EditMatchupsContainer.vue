<template>
<div class="col-md-12 allocation-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate">

    <template v-for="(team, index) in debate.teams">
      <team-draggable :team="team" :slot="index"> </team-draggable>
    </template>

  </debate>

  <unallocated-container>

    <div v-for="unallocated in unallocatedItems">
      <team-draggable :team="unallocated"> </team-draggable>
    </div>

  </unallocated-container>

</div>
</template>

<script>
import DrawContainer from '../mixins/DrawContainer.vue'
import DrawHeader from '../base/DrawHeader.vue'
import Debate from './Debate.vue'
import UnallocatedContainer from '../base/UnallocatedContainer.vue'
import TeamDraggable from '../draganddrops/TeamDraggable.vue'
import _ from 'lodash'


export default {
  components: {
    DrawHeader, Debate, UnallocatedContainer, TeamDraggable
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
