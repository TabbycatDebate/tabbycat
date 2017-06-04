<template>
<div class="col-md-12 draw-container">

  <div class="vertical-spacing" id="messages-container"></div>

  <constraints-slideover :venue="slideSubject" :constraints="slideInfo"></constraints-slideover>

  <draw-header :positions="positions">
    <div class="thead flex-cell flex-12 vue-droppable-container" data-toggle="tooltip" title="test" slot="hvenue">
      <span>Venue</span>
    </div>
  </draw-header>

  <debate v-for="debate in debates" :debate="debate" :key="debate.id">
    <div class="draw-cell flex-12 vue-droppable-container" slot="svenue">
      <generic-droppable>
        <slot name="svenue">
          <venue-draggable v-if="debate.venue !== null" :venue="debate.venue"></venue-draggable>
        </slot>
      </generic-droppable>
    </div>
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
import ConstraintsSlideover from '../slideovers/ConstraintsSlideover.vue'
import _ from 'lodash'


export default {
  mixins: [
    DrawContainer
  ],
  components: {
    UnallocatedContainer, DrawHeader, Debate, GenericDroppable,
    VenueDraggable, ConstraintsSlideover
  },
  props: {
    venueConstraints: Array,
  },
  computed: {
  },
  methods: {
    annotateSlideInfo(venue) {
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
    }
  },
  events: {
  }
}

</script>
