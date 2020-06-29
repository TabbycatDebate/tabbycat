<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems"
                        :unallocatedComponent="unallocatedComponent"
                        :handle-unused-drop="moveVenue">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount" allocate="true"
                           @show-allocate="showAllocate">
      <template slot="default-highlights">
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Constraint')"
                :title="gettext('This adjudicator or team has an unmet room constraint.')"></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Incomplete')"
                :title="gettext('Debate has no room.')"></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in sortedDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <droppable-item slot="venue" :handle-drop="moveVenue" :drop-context="{ 'assignment': debate.id }"
                        class="flex-12 flex-truncate border-right d-flex flex-wrap">
          <draggable-venue v-if="debate.venue" :item="allVenues[debate.venue]" class="flex-fill"
                           :drag-payload="{ 'item': debate.venue, 'assignment': debate.id }">
          </draggable-venue>
        </droppable-item>
      </drag-and-drop-debate>
    </template>

    <template slot="modals">
      <modal-for-allocating-venues :intro-text="gettext(allocateIntro)"
                                   :context-of-action="'allocate_debate_venues'">
      </modal-for-allocating-venues>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../templates/allocations/DragAndDropContainerMixin.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'

import ModalForAllocatingVenues from './ModalForAllocatingVenues.vue'
import DraggableVenue from './DraggableVenue.vue'

export default {
  components: { ModalForAllocatingVenues, DraggableVenue, DroppableItem },
  mixins: [DragAndDropContainerMixin],
  data: function () {
    return {
      highlights: {
        priority: {
          label: 'Priority',
          active: false,
          options: [],
        },
        category: {
          label: 'Category',
          active: false,
          options: [],
        },
      },
      allocateIntro: 'TKTK',
      unallocatedComponent: DraggableVenue,
    }
  },
  computed: {
    allVenues () {
      return this.$store.getters.allocatableItems
    },
  },
  methods: {
    getDebate: function (debateID) {
      if (debateID === null) {
        return null // Moving to or from Unused
      }
      let debate = this.allDebatesOrPanels[debateID]
      debate = JSON.parse(JSON.stringify(debate)) // Clone so non-reactive
      return debate
    },
    moveVenue: function (dragData, dropData) {
      const venueChanges = []
      const fromDebate = this.getDebate(dragData.assignment)
      const toDebate = this.getDebate(dropData.assignment)
      if (fromDebate !== null) { // Not moving FROM Unused
        fromDebate.venue = null
      }
      if (toDebate !== null) { // Moving to an actual debate
        if (toDebate.venue !== null && fromDebate !== null) {
          fromDebate.venue = toDebate.venue // Straight swap between two debates
        }
        toDebate.venue = dragData.item
      }
      // Send results
      if (fromDebate !== null) {
        venueChanges.push({ id: fromDebate.id, venue: fromDebate.venue })
      }
      if (toDebate !== null && dragData.assignment !== dropData.assignment) {
        venueChanges.push({ id: toDebate.id, venue: toDebate.venue })
      }
      this.$store.dispatch('updateDebatesOrPanelsAttribute', { venues: venueChanges })
      this.$store.dispatch('updateAllocableItemModified', [dragData.item])
    },
    getUnallocatedItemFromDebateOrPanel (debateOrPanel) {
      // Return the ID of the venue in this debate
      if (debateOrPanel.venue) {
        return [Number(debateOrPanel.venue)]
      } else {
        return []
      }
    },
  },
}
</script>
