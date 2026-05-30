<script setup>
import { computed } from 'vue'
import DragAndDropDebate from '../../templates/allocations/DragAndDropDebate.vue'
import DragAndDropLayout from '../../templates/allocations/DragAndDropLayout.vue'
import DragAndDropActions from '../../templates/allocations/DragAndDropActions.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDragAndDropContainer } from '../../templates/composables/useDragAndDropContainer.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

import ModalForAllocatingVenues from './ModalForAllocatingVenues.vue'
import DraggableVenue from './DraggableVenue.vue'

const props = defineProps({
  initialData: Object,
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const getUnallocatedItemFromDebateOrPanel = (debateOrPanel) => {
  if (debateOrPanel.venue) {
    return [Number(debateOrPanel.venue)]
  }
  return []
}

const container = useDragAndDropContainer({
  initialData: props.initialData,
  getUnallocatedItemFromDebateOrPanel,
})

const unallocatedComponent = DraggableVenue
const allocateIntro = 'TKTK'

const allVenues = computed(() => store.allocatableItems)

const maxTeams = computed(() => {
  return Math.max(...container.sortedDebatesOrPanels.value.map(d => d.teams ? d.teams.length : 0), 2)
})

const groupedDebatesByRound = computed(() => {
  const groups = {}
  const roundSlugForWSPath = props.initialData?.round?.seq
  for (const d of container.sortedDebatesOrPanels.value) {
    const seq = d.round_seq ?? roundSlugForWSPath
    if (!Object.prototype.hasOwnProperty.call(groups, seq)) {
      groups[seq] = { round_seq: seq, round_name: d.round_name, debates: [] }
    }
    groups[seq].debates.push(d)
  }
  return Object.values(groups).sort((a, b) => Number(a.round_seq) - Number(b.round_seq))
})

const getDebate = (debateID) => {
  if (debateID === null) {
    return null
  }
  let debate = container.allDebatesOrPanels.value[debateID]
  debate = JSON.parse(JSON.stringify(debate))
  return debate
}

const moveVenue = (dragData, dropData) => {
  const venueChanges = []
  const fromDebate = getDebate(dragData.assignment)
  const toDebate = getDebate(dropData.assignment)
  if (fromDebate !== null) {
    fromDebate.venue = null
  }
  if (toDebate !== null) {
    if (toDebate.venue !== null && fromDebate !== null) {
      fromDebate.venue = toDebate.venue
    }
    toDebate.venue = dragData.item
  }
  if (fromDebate !== null) {
    venueChanges.push({ id: fromDebate.id, venue: fromDebate.venue })
  }
  if (toDebate !== null && dragData.assignment !== dropData.assignment) {
    venueChanges.push({ id: toDebate.id, venue: toDebate.venue })
  }
  store.updateDebatesOrPanelsAttribute({ venues: venueChanges })
  store.updateAllocatableItemModified([dragData.item])
}

const showAllocate = () => {
  window.$?.('#confirmAllocateModal').modal('show')
}

const debatesOrPanelsCount = container.debatesOrPanelsCount
const unallocatedItems = container.unallocatedItems
</script>

<template>
  <drag-and-drop-layout
    :unallocated-items="unallocatedItems"
    :unallocated-component="unallocatedComponent"
    :handle-unused-drop="moveVenue"
  >
    <template #actions>
      <drag-and-drop-actions
        :count="debatesOrPanelsCount"
        allocate="true"
        @show-allocate="showAllocate"
      >
        <template #default-highlights>
          <button
            class="btn conflictable conflicts-toolbar hover-adjudicator"
            data-toggle="tooltip"
            :title="gettext('This adjudicator or team has an unmet room constraint.')"
          >
            {{ gettext('Constraint') }}
          </button>
          <button
            class="btn panel-incomplete"
            data-toggle="tooltip"
            :title="gettext('Debate has no room.')"
          >
            {{ gettext('Incomplete') }}
          </button>
        </template>
      </drag-and-drop-actions>
    </template>

    <template #debates>
      <div
        v-for="(group, gi) in groupedDebatesByRound"
        :key="'r-' + group.round_seq"
        class="mb-4"
      >
        <div
          v-if="groupedDebatesByRound.length > 1"
          class="mt-2 mb-3"
        >
          <hr
            v-if="gi > 0"
            class="my-3"
          >
          <div class="text-muted small">
            {{ group.round_name }}
          </div>
        </div>
        <drag-and-drop-debate
          v-for="debate in group.debates"
          :key="debate.id"
          :debate-or-panel="debate"
          :max-teams="maxTeams"
        >
          <template #venue>
            <droppable-item
              :handle-drop="moveVenue"
              :drop-context="{ 'assignment': debate.id }"
              class="flex-12 flex-truncate border-right d-flex flex-wrap"
            >
              <draggable-venue
                v-if="debate.venue"
                :item="allVenues[debate.venue]"
                class="flex-fill"
                :drag-payload="{ 'item': debate.venue, 'assignment': debate.id }"
                :debate-or-panel-id="debate.id"
              />
            </droppable-item>
          </template>
        </drag-and-drop-debate>
      </div>
    </template>

    <template #modals>
      <modal-for-allocating-venues
        :intro-text="gettext(allocateIntro)"
        :context-of-action="'allocate_debate_venues'"
      />
    </template>
  </drag-and-drop-layout>
</template>
