<template>
  <div>

    <section class="vc-header">
      <slot name="actions"></slot><!-- Actions -->
      <div class="" id="messages-container"><!-- Messages container--></div>
      <slot name="extra-messages"></slot>
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
