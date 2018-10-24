<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems" :unallocatedComponent="unallocatedComponent">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount"></drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in allDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <template slot="teams">fancy teams UI</template>
      </drag-and-drop-debate>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'

import DraggableTeam from './DraggableTeam.vue'

export default {
  mixins: [DragAndDropContainerMixin],
  data: () => ({
    unallocatedComponent: DraggableTeam,
  }),
  methods: {
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
