<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems" :unallocatedComponent="unallocatedComponent">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount"></drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in allDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <div slot="teams" class="flex-12 flex-truncate border-right d-flex flex-wrap">

          <droppable-item v-for="side in sides" :handle-drop="handleTeamDrop" :key="side"
                          :drop-context="{ 'assignment': debate.id, 'position': side }">
            <draggable-team v-if="debate.teams[side]" :item="allTeams[debate.teams[side]]" class="flex-fill"
                            :drag-payload="{ 'item': debate.teams[side], 'assignment': debate.id, 'position': side }">
            </draggable-team>
          </droppable-item>

        </div>

      </drag-and-drop-debate>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import DroppableItem from '../../utils/templates/DroppableItem.vue'

import DraggableTeam from './DraggableTeam.vue'

export default {
  components: { DraggableTeam, DroppableItem },
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
    handleTeamDrop: function (droppedData) {
      console.log('handledrop', droppedData)
      // Emit the 'send adj to this debate method'
    },
    getUnallocatedItemFromDebateOrPanel (debateOrPanel) {
      // Provide an array of IDs representing teams in this debate
      let itemIDs = []
      for (const positionDebateTeamID of Object.entries(debateOrPanel.teams)) {
        itemIDs.push(Number(positionDebateTeamID[1]))
      }
      return itemIDs
    },
  },
}
</script>
