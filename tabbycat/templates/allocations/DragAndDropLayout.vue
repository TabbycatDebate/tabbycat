<script setup>
import DragAndDropUnallocatedItems from './DragAndDropUnallocatedItems.vue'
import HoverPanel from './HoverPanel.vue'
import { onBeforeUnmount } from 'vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'
import { useDragAndDropStore } from './DragAndDropStore.js'

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()
const cancelSelection = (event) => {
  if (event.key === 'Escape' && (store.selectedAllocationItem || store.selectedAllocationTarget)) {
    store.clearAllocationSelection()
  }
}
onBeforeUnmount(() => store.clearAllocationSelection())
// The master layout for drag and drop screens; to using slots for content

defineProps(['unallocatedItems', 'unallocatedComponent', 'handleUnusedDrop', 'handlePanelSwap'])
</script>

<template>
  <div @keydown="cancelSelection">
    <section class="vc-header">
      <slot name="actions" /><!-- Actions -->
      <p class="small text-muted px-2 mb-1">
        {{ gettext('Tap an item and a destination to allocate, in either order. Tap again to deselect.') }}
        {{ gettext('Keyboard: Tab to navigate, Enter or Space to select, Escape to cancel.') }}
      </p>
      <p
        class="small px-2 mb-1"
        role="status"
        aria-live="polite"
      >
        <span v-if="store.selectedAllocationItem">{{ gettext('Item selected. Choose a destination.') }}</span>
        <span v-else-if="store.selectedAllocationTarget">{{ gettext('Destination selected. Choose an item.') }}</span>
      </p>
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
