<template>
  <div class="col-md-12 draw-container">

    <div class="row nav-pills">
      <a class="btn btn-default submit-disable" :href="roundInfo.backUrl">
        <span class="glyphicon glyphicon-chevron-left"></span> Back to Draw
      </a>
      <button class="btn btn-primary submit-disable" @click="createAutoAllocation">
        Auto Allocate
      </button>
      <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
    </div>

    <div class="row vertical-spacing">
      <div id="messages-container"></div>
    </div>

    <div class="vertical-spacing">
      <draw-header :positions="roundInfo.positions">
        <div class="thead flex-cell flex-12 vue-droppable-container" slot="hvenue">
          <span>Venue</span>
        </div>
      </draw-header>
      <debate v-for="debate in debates" :debate="debate" :key="debate.id" :round-info="roundInfo">
        <div class="draw-cell flex-12 vue-droppable-container" slot="svenue">
          <droppable-generic>
            <slot name="svenue">
              <draggable-venue v-if="debate.venue !== null"
               :venue="debate.venue" :debate-id="debate.id"></draggable-venue>
            </slot>
          </droppable-generic>
        </div>
      </debate>
    </div>

    <unallocated-items-container>
      <div v-for="unallocatedVenue in unallocatedVenuesByPriority">
        <draggable-venue :venue="unallocatedVenue"></draggable-venue>
      </div>
    </unallocated-items-container>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import DraggableVenue from '../draganddrops/DraggableVenue.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin],
  components: { DraggableVenue },
  props: { venueConstraints: Array },
  computed: {
    unallocatedVenuesByPriority: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['priority']))
    }
  },
  methods: {
    annotateSlideInfo(venue) {
      // Build array of this venue's categories as IDs
      var category_ids = _.map(venue.categories, 'id')
      if (category_ids.length > 0) {
        // Match IDs to venue constraint categories
        return _.filter(this.venueConstraints, function(vc) {
          return _.includes(category_ids, vc.id)
        });
      } else {
        return null
      }
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      var venue = this.debatesById[payload.debate].venue
      this.debatesById[payload.debate].venue = null
      this.unallocatedItems.push(venue) // Need to push; not append
    },
    createAutoAllocation: function(event) {
      var self = this
      $(event.target).button('loading')
      $.post({
        url: this.roundInfo.autoUrl,
        success: function(data, textStatus, jqXHR) {
          $.fn.showAlert('success', '<strong>Success:</strong> loaded the auto allocation', 10000)
          self.$eventHub.$emit('update-allocation', JSON.parse(data.debates))
          self.$eventHub.$emit('update-unallocated', JSON.parse(data.unallocatedVenues))
          self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
          $(event.target).button('reset')
        },
        error: function(data, textStatus, jqXHR) {
          $.fn.showAlert('danger', '<strong>Auto Allocation failed:</strong> ' + data.responseText, 0)
        },
        dataType: "json"
      });
    },
  }
}
</script>