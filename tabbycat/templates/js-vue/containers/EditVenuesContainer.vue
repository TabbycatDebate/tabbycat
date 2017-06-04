<template>
  <div class="col-md-12 draw-container">

    <div class="vertical-spacing" id="messages-container"></div>

    <!-- <constraints-slideover :venue="slideSubject" :constraints="slideInfo"></constraints-slideover> -->
    <!-- <team-slideover :team="slideSubject"></team-slideover> -->

    <draw-header :positions="positions">
      <div class="thead flex-cell flex-12 vue-droppable-container" data-toggle="tooltip" title="test" slot="hvenue">
        <span>Venue</span>
      </div>
    </draw-header>

    <debate v-for="debate in debates" :debate="debate" :key="debate.id">
      <div class="draw-cell flex-12 vue-droppable-container" slot="svenue">
        <droppable-generic>
          <slot name="svenue">
            <draggable-venue v-if="debate.venue !== null" :venue="debate.venue"></draggable-venue>
          </slot>
        </droppable-generic>
      </div>
    </debate>

    <unallocated-items-container>
      <div v-for="unallocatedVenue in unallocatedItems">
        <draggable-venue :venue="unallocatedVenue"></draggable-venue>
      </div>
    </unallocated-items-container>

  </div>
</template>

<script>
import DrawContainer from '../containers/DrawContainer.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableVenue from '../draganddrops/DraggableVenue.vue'
// import ConstraintsSlideover from '../slideovers/ConstraintsSlideOver.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainer],
  components: {
    UnallocatedItemsContainer, DrawHeader, Debate, DroppableGeneric,
    DraggableVenue, // ConstraintsSlideover
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