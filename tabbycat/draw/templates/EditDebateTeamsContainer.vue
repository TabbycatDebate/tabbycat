<script setup>
import { computed } from 'vue'
import DragAndDropDebate from '../../templates/allocations/DragAndDropDebate.vue'
import DragAndDropLayout from '../../templates/allocations/DragAndDropLayout.vue'
import DragAndDropActions from '../../templates/allocations/DragAndDropActions.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDragAndDropContainer } from '../../templates/composables/useDragAndDropContainer.js'

import DraggableTeam from './DraggableTeam.vue'
import DebateSideStatus from './DebateSideStatus.vue'

const props = defineProps({
  initialData: Object,
})

const store = useDragAndDropStore()

const getUnallocatedItemFromDebateOrPanel = (debateOrPanel) => {
  const itemIDs = []
  for (const positionDebateTeamID of Object.entries(debateOrPanel.teams)) {
    itemIDs.push(Number(positionDebateTeamID[1]))
  }
  return itemIDs
}

const container = useDragAndDropContainer({
  initialData: props.initialData,
  getUnallocatedItemFromDebateOrPanel,
})

const unallocatedComponent = DraggableTeam

const sides = computed(() => store.tournament.sides)
const allTeams = computed(() => store.allocatableItems)

const getDebateTeams = (debateID) => {
  if (debateID === null) {
    return null
  }
  let debateTeams = container.allDebatesOrPanels.value[debateID].teams
  debateTeams = JSON.parse(JSON.stringify(debateTeams))
  return debateTeams
}

const moveTeam = (dragData, dropData) => {
  const teamChanges = []
  const fromDebateTeams = getDebateTeams(dragData.assignment)
  let toDebateTeams = getDebateTeams(dropData.assignment)
  if (dragData.assignment === dropData.assignment) {
    toDebateTeams = fromDebateTeams
  }

  if (fromDebateTeams !== null) {
    fromDebateTeams[dragData.position] = null
  }
  if (toDebateTeams !== null) {
    if (toDebateTeams[dropData.position] !== null && fromDebateTeams !== null) {
      fromDebateTeams[dragData.position] = toDebateTeams[dropData.position]
    }
    toDebateTeams[dropData.position] = dragData.item
  }

  if (fromDebateTeams !== null) {
    teamChanges.push({ id: dragData.assignment, teams: fromDebateTeams })
  }
  if (toDebateTeams !== null && dragData.assignment !== dropData.assignment) {
    teamChanges.push({ id: dropData.assignment, teams: toDebateTeams })
  }

  store.updateDebatesOrPanelsAttribute({ teams: teamChanges })
  store.updateAllocatableItemModified([dragData.item])
}

const { allDebatesOrPanels, sortedDebatesOrPanels, debatesOrPanelsCount, unallocatedItems } = container
</script>

<template>
  <drag-and-drop-layout
    :unallocated-items="unallocatedItems"
    :unallocated-component="unallocatedComponent"
    :handle-unused-drop="moveTeam"
  >
    <template #actions>
      <drag-and-drop-actions :count="debatesOrPanelsCount" />
    </template>

    <template #extra-messages>
      <div
        id="alertdiv"
        class="alert alert-warning show"
      >
        <button
          type="button"
          class="close"
          data-dismiss="alert"
          aria-label="Close"
        >
          <span aria-hidden="true">×</span>
        </button>
        <span>{{ gettext(`Note: You should almost certainly not being using this page once results
                               have been released. Be sure to fill all gaps before leaving.`) }}</span>
      </div>
    </template>

    <template #debates>
      <drag-and-drop-debate
        v-for="debate in sortedDebatesOrPanels"
        :key="debate.id"
        :debate-or-panel="debate"
      >
        <!-- Hide for space — things get stretched in BP sides editing-->
        <template #liveness>
          <div />
        </template>
        <template #importance>
          <div />
        </template>

        <template #teams>
          <div
            :class="[sides.count > 2 ? 'flex-36' : 'flex-52',
                     'flex-truncate border-right d-flex flex-nowrap']"
          >
            <droppable-item
              v-for="(team, side) in allDebatesOrPanels[debate.id].teams"
              :key="side"
              :handle-drop="moveTeam"
              :drop-context="{ 'assignment': debate.id, 'position': side }"
              class="flex-5 flex-truncate"
            >
              <draggable-team
                v-if="team"
                :item="allTeams[team]"
                class="flex-fill"
                :drag-payload="{ 'item': team, 'assignment': debate.id, 'position': side }"
              />
            </droppable-item>

            <debate-side-status :debate="debate" />
          </div>
        </template>
      </drag-and-drop-debate>
    </template>
  </drag-and-drop-layout>
</template>
