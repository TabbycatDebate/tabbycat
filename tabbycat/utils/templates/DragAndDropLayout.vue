<template>
  <div>

    <section class="vc-header">
      <slot name="actions"></slot><!-- Actions -->
      <div class="" id="messages-container"><!-- Messages container--></div>
    </section>

    <section class="vc-debates-container border-top">
      <slot name="headers"></slot><!-- Debates Header -->
      <slot name="debates"></slot><!-- Debates -->
    </section>

    <drag-and-drop-unallocated-items :unallocatedItems="unallocatedItems"
                                     :unallocatedComponent="unallocatedComponent"
                                     :handle-unused-drop="handleUnusedDrop">
    </drag-and-drop-unallocated-items>

    <slot name="modals"></slot>

    <hover-panel></hover-panel>

  </div>
</template>

<script>
import DragAndDropUnallocatedItems from './DragAndDropUnallocatedItems.vue'
import HoverPanel from './HoverPanel.vue'
// The master layout for drag and drop screens; to using slots for content

export default {
  components: { DragAndDropUnallocatedItems, HoverPanel },
  props: ['unallocatedItems', 'unallocatedComponent', 'handleUnusedDrop'],
}
</script>

<style>
  .vc-header {
    min-height: 118px; /* Need to accomodate messages without resizing vertically */
    margin: 0 -7px; /* Stretch to meet full window width */
    padding-top: 52px; /* Push down notifications below toolbar */
    padding-bottom: 8px; /* Push down notifications below toolbar */
  }
  .vc-header .alert {
    margin-top: 8px; /* Override default to tighten */
    margin-bottom: 0px; /* Use bottom padding as per above */
  }
  .vc-debates-container {
    padding-bottom: 420px; /* Need to ensure unallocated doesn't overlap; matches its max height */
    margin: 0 -15px; /* Remove the container padding added from base layout */
  }
</style>
