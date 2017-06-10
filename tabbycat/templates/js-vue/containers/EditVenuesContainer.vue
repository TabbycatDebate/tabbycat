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
          <droppable-generic :assignment-id="debate.id">
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
import AjaxMixin from '../draganddrops/AjaxMixin.vue'
import DraggableVenue from '../draganddrops/DraggableVenue.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin, DrawContainerMixin],
  components: { DraggableVenue },
  props: { venueConstraints: Array },
  computed: {
    unallocatedVenuesByPriority: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['priority']))
    },
    venuesById: function() {
      var allDebateVenues = _.map(this.debates, function(debate) {
        return debate.venue
      })
      var validDebateVenues = _.filter(allDebateVenues, function(venue) {
        return venue !== null
      })
      return _.keyBy(validDebateVenues.concat(this.unallocatedItems), 'id')
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
    saveMove(venueId, fromDebateId, toDebateId, dontPushToUnused=false, isSwap=false) {
      var venue = this.venuesById[venueId]
      var toDebate = this.debatesById[toDebateId]
      var fromDebate = this.debatesById[fromDebateId]

      if (_.isUndefined(fromDebate)) { // Undefined if coming from unused
        var from = 'unused'
      } else {
        var from = fromDebate.id
      }
      if (_.isUndefined(toDebate)) { // Undefined if going to unused
        var to = 'unused'
      } else {
        var to = toDebate.id
      }

      var message = 'moved venue ' + venue.name + ' from ' + from + ' to ' + to
      var payload = { moved_item: venue.id, moved_from: from, moved_to: to }
      var self = this
      this.ajaxSave(this.roundInfo.saveUrl, payload, message, function() {
        if (to === 'unused') {
          self.processMoveToUnusedFromDebate(venue, fromDebate, dontPushToUnused)
        } else {
          if (from === 'unused') {
            self.processMoveToDebateFromUnused(venue, toDebate)
          } else {
            if (toDebate.venue === null) {
              self.processMoveToDebateWithoutVenueFromDebate(venue, fromDebate, toDebate)
            } else {
              self.processMoveToDebateWithVenueFromDebate(venue, fromDebate, toDebate, isSwap)
            }
          }
        }
      })
    },
    moveToDebate(payload, assignedId) {
      if (payload.debate === assignedId) {
        return // Moving to debate to debate; do nothing
      }
      this.saveMove(payload.venue, payload.debate, assignedId)
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      this.saveMove(payload.venue, payload.debate, null)
    },
    processMoveToUnusedFromDebate(venue, fromDebate, dontPushToUnused) {
      // Moving to Unused from a debate
      if (!dontPushToUnused) {
        // We don't push to unused when this venue is being removed from an
        // existing debate; ie via processMoveToDebateWithoutVenueFromDebate()
        this.unallocatedItems.push(venue) // Need to push; not append
      }
      fromDebate.venue = null
    },
    processMoveToDebateFromUnused(venue, toDebate) {
      // If moving from unused needed to remove the venue from unallcoated items
      var index = this.unallocatedItems.indexOf(venue)
      this.unallocatedItems.splice(index, 1)
      toDebate.venue = venue
    },
    processMoveToDebateWithoutVenueFromDebate(venue, fromDebate, toDebate) {
      // If moving from an existing debate without a venue then retrigger a save
      // as if we were moving to unused but override adding it back to the js data
      toDebate.venue = venue
      this.saveMove(venue.id, fromDebate.id, 'unused', true)
    },
    processMoveToDebateWithVenueFromDebate(venue, fromDebate, toDebate, isSwap) {
      // If moving from one debate to another where both have venues
      // The isSwap override is here to prevent never ending recursive recalls
      // If moving from an existing debate into a debate with a venue; do a swap
      if (!isSwap) {
        this.saveMove(toDebate.venue.id, toDebate.id, fromDebate.id, false, true)
      }
      toDebate.venue = venue
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