<template>

  <drag-and-drop-layout>

    <drag-and-drop-actions slot="actions"></drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in debatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <template slot="teams">fancy teams UI</template>
      </drag-and-drop-debate>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'

export default {
  mixins: [DragAndDropContainerMixin],
}
</script>
