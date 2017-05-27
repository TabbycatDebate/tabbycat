<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <venue-constraints-slideover :venue="slideSubject" :constraints="slideConstraints"></venue-slideover>

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
import VenuesConstraintSlideover from '../slideovers/VenuesConstraintSlideover.vue'
import _ from 'lodash'


export default {
  components: {
    UnallocatedContainer, DrawHeader, Debate, GenericDroppable,
    VenueDraggable, VenuesConstraintSlideover
  },
  created: function () {
    this.$eventHub.$on('set-slideover', this.setSlideover)
    this.$eventHub.$on('unset-slideover', this.unsetSlideover)
  },
  data: function() {
    return {
      slideSubject: null,
      slideConstraints: null
    }
  },
  mixins: [
    DrawContainer
  ],
  props: {
    venueConstraints: Array,
  },
  computed: {
  },
  methods: {
    getConstraintsForVenue(venue) {
      // Build array of this venue's categories as IDs
      var category_ids = _.map(venue.categories, 'id')
      if (category_ids.length > 0) {
        // Match IDs to venue constraint categories
        return _.filter(this.venueConstraints, function(vc) {
          return _.includes(category_ids, vc.id);
        });
      } else {
        return null
      }
    },
    setSlideover: function(venue) {
      this.slideSubject = venue
      this.slideConstraints = this.getConstraintsForVenue(venue)
    },
    unsetSlideover: function() {
      // this.slideSubject = null
      // this.slideConstraints = null
    },
  },
  events: {
  }
}

</script>
