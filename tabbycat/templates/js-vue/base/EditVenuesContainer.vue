<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate">
    <venue-draggable slot="svenue" :venue="debate.venue"></venue-draggable>
  </debate>

  <unallocated-container>

    <div v-for="unallocatedVenue in unallocatedItems">
      <venue-draggable :venue="unallocatedVenue"></venue-draggable>
    </div>

  </unallocated-container>

</div>
</template>

<script>
import DrawContainer from '../mixins/DrawContainer.vue'
import UnallocatedContainer from '../base/UnallocatedContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import VenueDraggable from '../draganddrops/VenueDraggable.vue'
import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate, VenueDraggable
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
