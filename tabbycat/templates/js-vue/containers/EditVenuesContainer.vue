<template>
  <div class="col-md-12 draw-container">

    <div class="row nav-pills">
      <a class="btn btn-default submit-disable" :href="backUrl">
        <span class="glyphicon glyphicon-chevron-left"></span> Back to Draw
      </a>
      <button class="btn btn-primary submit-disable" type="submit">
        Auto Allocate
      </button>
      <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
    </div>

    <div class="row">
      <div class="vertical-spacing" id="messages-container"></div>
    </div>

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

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableVenue from '../draganddrops/DraggableVenue.vue'
import SlideOverItem from '../infoovers/SlideOverItem.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin],
  components: {
    UnallocatedItemsContainer, DrawHeader, Debate, DroppableGeneric,
    DraggableVenue, SlideOverItem, AutoSaveCounter
  },
  props: { venueConstraints: Array },
  computed: { },
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
    },
    moveToUnused() {
      console.log('moveVenueToUnused')
    }
  },
  events: {
  }
}
</script>