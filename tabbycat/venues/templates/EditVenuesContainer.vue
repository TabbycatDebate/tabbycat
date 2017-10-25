<template>
  <div class="draw-container">

    <div class="row page-navs">
      <div class="col d-flex justify-content-between">
        <a class="btn btn-outline-primary " :href="roundInfo.backUrl">
          <i data-feather="chevron-left"></i> Back to Draw
        </a>
        <button class="btn btn-success " @click="createAutoAllocation">
          Auto Allocate all Venues
        </button>
        <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
      </div>
    </div>

    <div class="mb-3 mt-3">
      <draw-header :round-info="roundInfo" @resort="updateSorting"
                   :sort-key="sortKey" :sort-order="sortOrder">
        <div @click="updateSorting('venue')" slot="hvenue"
             class="vue-sortable thead flex-cell flex-12 ">
          <span>Venue </span>
          <span :class="sortClasses('venue')"></span>
        </div>
      </draw-header>
      <debate v-for="debate in dataOrderedByKey"
              :debate="debate" :key="debate.id" :round-info="roundInfo">
        <div class="draw-cell droppable-cell flex-12 vue-droppable-container"
             slot="svenue">
          <droppable-generic :assignment-id="debate.id" :locked="debate.locked">
            <slot name="svenue">
              <draggable-venue v-if="debate.venue !== null"
               :venue="debate.venue" :debate-id="debate.id"
               :locked="debate.locked"></draggable-venue>
          </slot>
          </droppable-generic>
        </div>
      </debate>
    </div>

    <unallocated-items-container>
      <div v-for="venue in unallocatedVenuesByPriority">
        <draggable-venue :venue="venue" :locked="venue.locked"></draggable-venue>
      </div>
    </unallocated-items-container>

    <slide-over :subject="slideOverSubject"></slide-over>

  </div>
</template>

<script>
import DrawContainerMixin from '../../draw/templates/DrawContainerMixin.vue'
import VenueMovingMixin from '../../templates/ajax/VenueMovingMixin.vue'
import DraggableVenue from '../../templates/draganddrops/DraggableVenue.vue'
import _ from 'lodash'

export default {
  mixins: [VenueMovingMixin, DrawContainerMixin],
  components: { DraggableVenue },
  props: { venueConstraints: Array },
  computed: {
    unallocatedVenuesByPriority: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['priority']))
    },
    allVenuesById: function() {
      return _.keyBy(this.venues.concat(this.unallocatedItems), 'id')
    },
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
    moveToDebate(payload, assignedId) {
      if (payload.debate === assignedId) {
        return // Moving to debate from that same debate; do nothing
      }
      this.saveMove(payload.venue, payload.debate, assignedId)
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      this.saveMove(payload.venue, payload.debate, null)
    },
    createAutoAllocation: function(event) {
      var self = this
      $.fn.loadButton(event.target)
      $.post({
        url: this.roundInfo.autoUrl,
        dataType: 'json',
      }).done(function(data, textStatus, jqXHR) {
        // Success handler
        self.$eventHub.$emit('update-allocation', JSON.parse(data.debates))
        self.$eventHub.$emit('update-unallocated', JSON.parse(data.unallocatedVenues))
        self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
        $.fn.showAlert('success', 'Successfully loaded the auto allocation', 10000)
        $.fn.resetButton(event.target)
      }).fail(function(response) {
        var info = response.responseJSON.message
        $.fn.showAlert('danger', 'Auto Allocation failed: ' + info, 0)
        $.fn.resetButton(event.target)
      })
    },
  }
}
</script>
