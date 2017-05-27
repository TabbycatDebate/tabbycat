<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <venue-slideover :venue="slideOverVenue"></venue-slideover>

  <draw-header :positions="positions"></draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">

    <generic-droppable slot="svenue">
      <venue-draggable v-if="debate.venue !== null" :venue="debate.venue"></venue-draggable>
    </generic-droppable>

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
import GenericDroppable from '../draganddrops/GenericDroppable.vue'
import VenueDraggable from '../draganddrops/VenueDraggable.vue'
import VenueSlideover from '../slideovers/VenueSlideover.vue'
import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate, GenericDroppable,
    VenueDraggable, VenueSlideover
  },
  created: function () {
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
  },
  data: function() {
    return {
      slideOverVenue: null
    }
  },
  mixins: [
    DrawContainer
  ],
  props: {
  },
  computed: {
  },
  methods: {
    setSlideover: function(venue) {
      this.slideOverVenue = venue
    },
    unsetSlideover: function() {
      this.slideOverVenue = null
    },
  },
  events: {
  }
}

</script>
