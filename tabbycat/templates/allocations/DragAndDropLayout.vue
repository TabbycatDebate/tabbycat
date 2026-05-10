<script setup>
import DragAndDropUnallocatedItems from './DragAndDropUnallocatedItems.vue'
import HoverPanel from './HoverPanel.vue'
// The master layout for drag and drop screens; to using slots for content

defineProps(['unallocatedItems', 'unallocatedComponent', 'handleUnusedDrop', 'handlePanelSwap'])
</script>

<template>
  <div>
    <section class="vc-header">
      <slot name="actions" /><!-- Actions -->
      <div
        id="messages-container"
        class=""
      >
        <!-- Messages container-->
      </div>
      <slot name="extra-messages" />
    </section>

    <section class="vc-debates-container border-top">
      <slot name="headers" /><!-- Debates Header -->
      <slot name="debates" /><!-- Debates -->
    </section>

    <drag-and-drop-unallocated-items
      :unallocated-items="unallocatedItems"
      :unallocated-component="unallocatedComponent"
      :handle-unused-drop="handleUnusedDrop"
    />

    <slot name="modals" />

    <hover-panel />
  </div>
</template>
