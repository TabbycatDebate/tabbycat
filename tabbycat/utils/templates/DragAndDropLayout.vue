<template>
  <div>

    <section>
      <slot name="actions"></slot><!-- Actions -->
    </section>

    <section class="vc-debates-container">
      <div id="messages-container"><!-- Messages container--></div>
      <slot name="headers"></slot><!-- Debates Header -->
      <slot name="debates"></slot><!-- Debates -->
    </section>

    <drag-and-drop-unallocated-items
      :unallocatedItems="unallocatedItems" :unallocatedComponent="unallocatedComponent">
    </drag-and-drop-unallocated-items>

    <slot name=""></slot><!-- SlideOver Item -->

    <slot name="modals"></slot>

  </div>
</template>

<script>
import DragAndDropUnallocatedItems from './DragAndDropUnallocatedItems.vue'
// The master layout for drag and drop screens; to using slots for content

export default {
  components: { DragAndDropUnallocatedItems },
  props: ['unallocatedItems', 'unallocatedComponent'],
}
</script>

<style scoped>
  .vc-debates-container {
    padding-top: 100px; /* Need to ensure actions bar doesn't overlap */
    padding-bottom: 100px; /* Need to ensure unallocated area doesn't overlap */
    margin: 0 -15px; /* Remove the container padding added from base layout */
  }
</style>
