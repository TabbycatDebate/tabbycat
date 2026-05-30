<script setup>
import { useDragAndDropStore } from './DragAndDropStore.js'
import { useDraggable } from '../composables/useDraggable.js'

// Passed down from the parent because the trigger for the show/hide needs to be on this element
const props = defineProps({
  locked: {
    type: Boolean,
    default: false,
  },
  dragPayload: Object,
  hoverPanel: {
    type: Boolean,
    default: false,
  },
  hoverPanelItem: Object,
  hoverPanelType: String,
  hoverConflicts: {
    type: Boolean,
    default: false,
  },
  hoverConflictsItem: Number,
  hoverConflictsType: String,
})

const store = useDragAndDropStore()
const { draggableClasses, dragStart, dragEnd, drag } = useDraggable(props)

const showHovers = () => {
  if (props.hoverPanel) {
    store.setHoverPanel({ subject: props.hoverPanelItem, type: props.hoverPanelType })
  }
  if (props.hoverConflicts) {
    let clashes = null
    let histories = null
    if (props.hoverConflictsType === 'team') {
      clashes = store.teamClashesForItem(props.hoverConflictsItem)
      histories = store.teamHistoriesForItem(props.hoverConflictsItem)
    } else if (props.hoverConflictsType === 'adjudicator') {
      clashes = store.adjudicatorClashesForItem(props.hoverConflictsItem)
      histories = store.adjudicatorHistoriesForItem(props.hoverConflictsItem)
    } else if (props.hoverConflictsType === 'panel') {
      clashes = store.panelClashesOrHistoriesForItem(props.hoverConflictsItem, 'clashes')
      histories = store.panelClashesOrHistoriesForItem(props.hoverConflictsItem, 'histories')
    }
    store.setHoverConflicts({ clashes: clashes, histories: histories })
  }
}

const hideHovers = () => {
  if (props.hoverPanel) {
    store.unsetHoverPanel()
  }
  if (props.hoverConflicts) {
    store.unsetHoverConflicts()
  }
}
</script>

<template>
  <div
    draggable="true"
    :class="['d-flex m-1 align-items-center align-self-center', draggableClasses]"
    @drag="drag"
    @dragstart="dragStart"
    @dragend="dragEnd"
    @mouseenter="showHovers"
    @mouseleave="hideHovers"
  >
    <slot>
      <h4 class="mb-0 py-1 text-monospace vc-draggable-number vc-number">
        <slot name="number" />
      </h4>
      <div class="py-1 pl-2 pr-2 d-flex flex-column flex-truncate">
        <h5 class="mb-0 vc-title text-truncate">
          <slot name="title" />
        </h5>
        <h6 class="mb-0 vue-draggable-muted vc-subtitle text-truncate">
          <slot name="subtitle" />
        </h6>
      </div>
      <slot name="tooltip" />
    </slot>
  </div>
</template>
