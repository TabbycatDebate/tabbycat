<template>
  <div class="draw-container allocation-container">

    <div id="messages-container"><!-- Messages container--></div>

    <section>
      <slot name="actions"></slot><!-- Actions -->
    </section>

    <section>
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
