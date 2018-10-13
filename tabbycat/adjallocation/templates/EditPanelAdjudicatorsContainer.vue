<template>

  <section>
    <drag-and-drop-debate v-for="panel in debatesOrPanels" :key="panel.id" :debateOrPanel="panel">
      <debate-importance slot="importance" :debateOrPanel="panel"></debate-importance>
      <template slot="adjudicators">fancy adjs UI</template>
      <template slot="venue"><span></span></template><!--Hide Venues-->
    </drag-and-drop-debate>
  </section>

</template>

<script>
import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
  data: function () {
    return {
      sockets: ['panels'], // Override the normal debate socket from DragAndDropContainerMixin
    }
  },
}
</script>
