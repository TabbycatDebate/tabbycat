<script setup>
import { computed } from 'vue'
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'

const props = defineProps({
  item: Object,
  dragPayload: Object,
  debateOrPanelId: {
    type: Number,
    default: null,
  },
  isTrainee: {
    type: Boolean,
    default: false,
  },
})

const store = useDragAndDropStore()

const highlightData = computed(() => props.item)
const { highlightsCSS } = useHighlightable({ highlightData })

const venueConstraintsCSS = computed(() => {
  try {
    if (!props.debateOrPanelId || !props.item || !props.item.categories) {
      return ''
    }
    const constraints = store.extra?.constraints?.debates?.[props.debateOrPanelId]
    if (!constraints || constraints.length === 0) {
      return ''
    }
    const venueCategoryIds = new Set(props.item.categories.map(c => (typeof c === 'object' ? c.id : c)))
    for (const allowedList of constraints) {
      let intersects = false
      for (const catId of allowedList) {
        if (venueCategoryIds.has(catId)) {
          intersects = true
          break
        }
      }
      if (!intersects) {
        return 'conflictable hover-adjudicator'
      }
    }
    return ''
  } catch (e) {
    return ''
  }
})

const hoverVenueConstraintCSS = computed(() => {
  try {
    const allowedSets = store.currentHoverVenueConstraintSets
    if (!allowedSets || allowedSets.length === 0) { return '' }
    const venueCategoryIds = new Set((props.item?.categories ?? []).map(c => (typeof c === 'object' ? c.id : c)))
    for (const allowed of allowedSets) {
      let intersects = false
      for (const cid of allowed) {
        if (venueCategoryIds.has(cid)) { intersects = true; break }
      }
      if (!intersects) {
        return 'conflictable hover-adjudicator'
      }
    }
    return ''
  } catch (e) {
    return ''
  }
})

const onVenueMouseEnter = () => {
  try {
    const cats = (props.item?.categories ?? []).map(c => (typeof c === 'object' ? c.id : c))
    store.setHoverVenue({ categories: cats, debateId: props.debateOrPanelId })
  } catch (e) {
    // noop
  }
}

const onVenueMouseLeave = () => {
  store.unsetHoverVenue()
}
</script>

<template>
  <draggable-item
    :drag-payload="dragPayload"
    :class="[{ 'bg-dark text-white': !item.available }, highlightsCSS, venueConstraintsCSS, hoverVenueConstraintCSS]"
    @mouseenter="onVenueMouseEnter"
    @mouseleave="onVenueMouseLeave"
  >
    <template #number>
      <span>
        <small class="pl-2 vue-draggable-muted ">{{ item.priority }}</small>
      </span>
    </template>
    <template #title>
      <span>
        {{ item.display_name }}
      </span>
    </template>
    <template #subtitle>
      <span />
    </template>
  </draggable-item>
</template>
