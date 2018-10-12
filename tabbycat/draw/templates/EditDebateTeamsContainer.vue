<template>

  <section>
    <drag-and-drop-debate v-for="debate in debatesOrPanels"
                          :key="debate.id" :debateOrPanel="debate">
      <template slot="teams">fancy teams UI</template>
    </drag-and-drop-debate>
  </section>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'

export default {
  mixins: [DragAndDropContainerMixin],
}
</script>
