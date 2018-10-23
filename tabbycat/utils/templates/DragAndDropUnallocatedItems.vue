<template>
  <div class="navbar-light fixed-bottom d-flex flex-column p-0">

    <droppable-item class="d-flex flex-column pb-2" @handledrop="handledrop">

      <section class="vc-resize-handler mx-auto mt-1 mb-1 text-center"
               data-toggle="tooltip" :title="gettext('Drag to resize')">
        <i data-feather="menu" class="align-self-center mx-auto"></i>
      </section>
        <div v-for="item in unallocatedItems" :is="unallocatedComponent"
             :item="item" :key="item.id"
             :payload="{ 'item': item.id, 'assignment': null, 'position': null }"></div>

    </droppable-item>

  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import DroppableMixin from './DroppableMixin.vue'
import DroppableItem from './DroppableItem.vue'

export default {
  mixins: [DroppableMixin],
  components: { DroppableItem },
  props: ['unallocatedItems', 'unallocatedComponent'],
  methods: {
    handledrop: function (droppedData) {
      console.log('handledrop', droppedData)
      // Copy existing allocation from VueX state
      let newAllocation = this.allDebatesOrPanels[droppedData.assignment].adjudicators
      newAllocation = JSON.parse(JSON.stringify(newAllocation)) // Clone so non-reactive
      // Loop over all adjudicator positions and remove matching adjudicators
      for (let [position, adjudicators] of Object.entries(newAllocation)) {
        newAllocation[position] = adjudicators.filter(adjID => adjID !== droppedData.item)
      }
      let allocationChanges = [{ 'id': droppedData.assignment, 'adjudicators': newAllocation }]
      this.$store.dispatch('updateDebatesOrPanelsAttribute', { 'adjudicators': allocationChanges })
    },
  },
  computed: {
    ...mapGetters(['allDebatesOrPanels']),
  },
}
</script>

<style scoped>
  .vc-resize-handler {
    height: 20px;
    width: 100%;
  }
  .vc-resize-handler:hover {
    cursor: ns-resize;
  }
</style>
