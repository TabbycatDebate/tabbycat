<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems"
                        :unallocatedComponent="unallocatedComponent"
                        :handle-unused-drop="moveTeam">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount"></drag-and-drop-actions>

   <template slot="extra-messages">
      <div id="alertdiv" class="alert alert-warning show">
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">×</span></button>
        <span v-text="gettext(`Note: You should almost certainly not being using this page once results
                               have been released. Be sure to fill all gaps before leaving.`)"></span>
      </div>
    </template>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in sortedDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">

        <!-- Hide for space — things get stretched in BP sides editing-->
        <div slot="liveness"></div>
        <div slot="importance"></div>

        <div slot="teams" :class="[sides.count > 2 ? 'flex-36' : 'flex-52',
                                   'flex-truncate border-right d-flex flex-nowrap']">

          <droppable-item v-for="side in sides" :handle-drop="moveTeam" :key="side"
                          :drop-context="{ 'assignment': debate.id, 'position': side }"
                          class="flex-5 flex-truncate">
            <draggable-team v-if="debate.teams[side]" :item="allTeams[debate.teams[side]]" class="flex-fill"
                            :drag-payload="{ 'item': debate.teams[side], 'assignment': debate.id, 'position': side }">
            </draggable-team>
          </droppable-item>

          <debate-side-status :debate="debate"></debate-side-status>

        </div>
      </drag-and-drop-debate>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../templates/allocations/DragAndDropContainerMixin.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'

import DraggableTeam from './DraggableTeam.vue'
import DebateSideStatus from './DebateSideStatus.vue'

export default {
  components: { DebateSideStatus, DraggableTeam, DroppableItem },
  mixins: [DragAndDropContainerMixin],
  data: () => ({
    unallocatedComponent: DraggableTeam,
  }),
  computed: {
    sides: function () {
      return this.$store.state.tournament.sides
    },
    allTeams () {
      return this.$store.getters.allocatableItems
    },
  },
  methods: {
    getDebateTeams: function (debateID) {
      if (debateID === null) {
        return null // Moving to or from Unused
      }
      let debateTeams = this.allDebatesOrPanels[debateID].teams
      debateTeams = JSON.parse(JSON.stringify(debateTeams)) // Clone so non-reactive
      return debateTeams
    },
    moveTeam: function (dragData, dropData) {
      // Emit the 'send adj to this debate method'
      const teamChanges = []
      const fromDebateTeams = this.getDebateTeams(dragData.assignment)
      let toDebateTeams = this.getDebateTeams(dropData.assignment)
      if (dragData.assignment === dropData.assignment) {
        toDebateTeams = fromDebateTeams // If repositioning we don't want two distinct allocations
      }

      if (fromDebateTeams !== null) { // Not moving FROM Unused
        fromDebateTeams[dragData.position] = null
      }
      if (toDebateTeams !== null) { // Not moving TO Unused
        if (toDebateTeams[dropData.position] !== null && fromDebateTeams !== null) { // Swap
          fromDebateTeams[dragData.position] = toDebateTeams[dropData.position]
        }
        toDebateTeams[dropData.position] = dragData.item
      }
      // Send results
      if (fromDebateTeams !== null) {
        teamChanges.push({ id: dragData.assignment, teams: fromDebateTeams })
      }
      if (toDebateTeams !== null && dragData.assignment !== dropData.assignment) {
        teamChanges.push({ id: dropData.assignment, teams: toDebateTeams })
      }
      this.$store.dispatch('updateDebatesOrPanelsAttribute', { teams: teamChanges })
      this.$store.dispatch('updateAllocableItemModified', [dragData.item])
    },
    getUnallocatedItemFromDebateOrPanel (debateOrPanel) {
      // Provide an array of IDs representing teams in this debate
      const itemIDs = []
      for (const positionDebateTeamID of Object.entries(debateOrPanel.teams)) {
        itemIDs.push(Number(positionDebateTeamID[1]))
      }
      return itemIDs
    },
  },
}
</script>
