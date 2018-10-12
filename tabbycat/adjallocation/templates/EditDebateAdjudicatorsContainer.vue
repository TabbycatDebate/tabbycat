<template>

  <section>
    <drag-and-drop-debate v-for="debate in debatesOrPanels"
                          :key="debate.id" :debateOrPanel="debate">
      <debate-importance slot="importance"></debate-importance>
      <template slot="adjudicators">fancy adjs UI</template>
      <template slot="venue"><span></span></template><!--Hide Venues-->
    </drag-and-drop-debate>
  </section>

</template>

<script>
import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
}
</script>
