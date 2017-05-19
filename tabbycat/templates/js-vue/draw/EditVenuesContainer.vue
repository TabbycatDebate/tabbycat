<template>
<div class="col-md-12 allocation-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate">
    <venue-draggable slot="venue" :venue="debate.venue"></venue-draggable>
  </debate>

  <unallocated-container>

    <div v-for="unallocated in unallocatedItems">
      <venue-draggable :venue="unallocated"></venue-draggable>
    </div>

  </unallocated-container>

</div>
</template>

<script>
import DrawContainer from '../mixins/DrawContainer.vue'
import DrawHeader from '../base/DrawHeader.vue'
import Debate from './Debate.vue'
import UnallocatedContainer from '../base/UnallocatedContainer.vue'
import VenueDraggable from '../draganddrops/VenueDraggable.vue'
import _ from 'lodash'


export default {
  components: {
    DrawHeader, Debate, UnallocatedContainer, VenueDraggable
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
