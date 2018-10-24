<template>
  <div class="navbar-light fixed-bottom d-flex border-top flex-column p-0 vc-unallocated-container">

    <droppable-item class="d-flex flex-column pt-2 px-2" :handle-drop="handleUnusedDrop"
                    :drop-context="{ 'assignment': null, 'position': null }">

      <section class="flex-fill pb-1 px-1 d-flex justify-content-between">
        <div class="small text-muted">{{ unallocatedItems.length }} unallocated</div>
        <i data-feather="menu" class="vc-resize-handler align-self-center mx-auto"
           data-toggle="tooltip" :title="gettext('Drag to resize')"></i>
        <div class="small text-muted">
          <span v-text="gettext('Sort By X')"></span><span v-text="gettext('Sort By Y')"></span>
        </div>
      </section>
      <section class="d-flex flex-wrap pb-2">
        <div v-for="item in unallocatedItems" :is="unallocatedComponent" :item="item" :key="item.id"
             :drag-payload="{ 'item': item.id, 'assignment': null, 'position': null }"></div>
      </section>

    </droppable-item>

  </div>
</template>

<script>
import DroppableMixin from './DroppableMixin.vue'
import DroppableItem from './DroppableItem.vue'

export default {
  mixins: [DroppableMixin],
  components: { DroppableItem },
  props: ['unallocatedItems', 'unallocatedComponent', 'handleUnusedDrop'],
}
</script>

<style scoped>
  .vc-unallocated-container {
    max-height: 50vh; /* Don't ever be more than 50% of the screen */
  }
  .vc-resize-handler:hover {
    cursor: ns-resize;
  }
</style>
