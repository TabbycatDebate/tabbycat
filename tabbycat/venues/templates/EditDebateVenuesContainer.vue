<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems" :unallocatedComponent="unallocatedComponent">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount" allocate="true" @show-allocate="showAllocate">
      <template slot="default-highlights">
        <button class="btn btn-outline-secondary disabled"><i data-feather="help-circle"></i></button>
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Constraint')"
                :title="gettext('This adjudicator or team has an unmet venue constraint.')"></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Incomplete')"
                :title="gettext('Debate has no venue.')"></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in allDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <droppable-item slot="venue" :handle-drop="handleVenueDrop" :drop-context="{ 'assignment': debate.id }"
                        class="flex-8 flex-truncate border-right d-flex flex-wrap">
          <draggable-venue v-if="debate.venue" :item="allVenues[debate.venue]" class="flex-fill"
                           :drag-payload="{ 'item': debate.venue, 'assignment': debate.id }">
          </draggable-venue>
        </droppable-item>
      </drag-and-drop-debate>
    </template>

    <template slot="modals">
      <modal-for-allocating :intro-text="gettext(allocateIntro)"
                            :context-of-action="'allocate_debate_venues'"></modal-for-allocating>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import ModalForAllocating from '../../utils/templates/modals/ModalForAllocating.vue'
import DroppableItem from '../../utils/templates/DroppableItem.vue'

import DraggableVenue from './DraggableVenue.vue'

export default {
  components: { ModalForAllocating, DraggableVenue, DroppableItem },
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
      allocateIntro: `TKTK`,
      unallocatedComponent: DraggableVenue,
    }
  },
  computed: {
    allVenues () {
      return this.$store.getters.allocatableItems
    },
  },
  methods: {
    handleVenueDrop: function (droppedData) {
      console.log('handledrop', droppedData)
      // Emit the 'send adj to this debate method'
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
