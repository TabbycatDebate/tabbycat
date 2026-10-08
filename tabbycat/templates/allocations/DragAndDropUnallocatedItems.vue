<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import DroppableItem from './DroppableItem.vue'
import { useDragAndDropStore } from './DragAndDropStore.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  unallocatedItems: { type: Array, default: () => [] },
  unallocatedComponent: { type: [Object, Function, String], required: true },
  handleUnusedDrop: { type: Function, required: true },
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const resizeableElement = ref(null)
const unallocatedHolder = ref(null)

const showUnavailable = ref(false)
const sorts = reactive({
  drag: { label: 'Sort By Drag Order', active: true },
  name: { label: 'Sort By Name', active: false },
  score: { label: 'Sort By Score', active: false },
})

const height = ref(null)
const minHeight = 55
const maxHeight = 300
const itemContainerHeight = ref(null)
const startPosition = ref(null)

const isVenue = computed(() => {
  return props.unallocatedItems?.[0] && 'priority' in props.unallocatedItems[0]
})

const isTeam = computed(() => {
  return props.unallocatedItems?.[0] && 'short_name' in props.unallocatedItems[0]
})

const filteredAll = computed(() => props.unallocatedItems)

const filteredAvailable = computed(() => {
  return props.unallocatedItems.slice(0).filter((item) => item.available)
})

const filteredUnallocatedItems = computed(() => {
  return showUnavailable.value ? filteredAll.value : filteredAvailable.value
})

const sortedUnallocatedItemsByOrder = computed(() => {
  return filteredUnallocatedItems.value.slice(0).sort((itemA, itemB) => {
    return itemB.vue_last_modified - itemA.vue_last_modified
  })
})

const sortedUnallocatedItemsByName = computed(() => {
  const field = isVenue.value ? 'display_name' : (isTeam.value ? 'short_name' : 'name')
  return filteredUnallocatedItems.value.slice(0).sort((itemA, itemB) => {
    return itemA[field].localeCompare(itemB[field])
  })
})

const sortedUnallocatedItemsByScore = computed(() => {
  const field = isVenue.value ? 'priority' : (isTeam.value ? 'points' : 'score')
  return filteredUnallocatedItems.value.slice(0).sort((itemA, itemB) => {
    return itemB[field] - itemA[field]
  })
})

const boundedHeight = (h) => {
  if (h > maxHeight) {
    return maxHeight
  } else if (h < minHeight) {
    return minHeight
  }
  return h
}

const activeSortKey = computed(() => {
  const active = Object.entries(sorts).find(([, v]) => v.active)
  return active ? active[0] : 'drag'
})

const currentSortingMethod = computed(() => {
  const key = activeSortKey.value
  if (key === 'name') return sortedUnallocatedItemsByName.value
  if (key === 'score') return sortedUnallocatedItemsByScore.value
  return sortedUnallocatedItemsByOrder.value
})

const setSort = (selectedKey) => {
  Object.keys(sorts).forEach(key => {
    sorts[key].active = selectedKey === key
  })
}

const resizeEnd = (_event) => {
  window.removeEventListener('mousemove', resizeMotion)
  window.removeEventListener('mouseup', resizeEnd)
}

const resizeMotion = (event) => {
  height.value = boundedHeight(window.innerHeight - event.clientY)
  if (height.value > maxHeight || height.value < minHeight) {
    resizeEnd(event)
  }
}

const resizeStart = (event) => {
  event.preventDefault()
  startPosition.value = event.clientY
  window.addEventListener('mousemove', resizeMotion)
  window.addEventListener('mouseup', resizeEnd)
}

const unsetHoverPanel = () => {
  store.unsetHoverPanel()
}

const unsetHoverConflicts = () => {
  store.unsetHoverConflicts()
}

onMounted(() => {
  if (resizeableElement.value) {
    height.value = boundedHeight(resizeableElement.value.clientHeight)
  }
  if (unallocatedHolder.value) {
    itemContainerHeight.value = unallocatedHolder.value.clientHeight
  }
  if (filteredAvailable.value.length === 0) {
    showUnavailable.value = true
  }
})

watch(() => props.unallocatedItems, async () => {
  await nextTick()
  if (!unallocatedHolder.value || itemContainerHeight.value === null || height.value === null) {
    return
  }
  if (unallocatedHolder.value.clientHeight < itemContainerHeight.value) {
    const difference = itemContainerHeight.value - unallocatedHolder.value.clientHeight
    let newHeight = boundedHeight(height.value - difference)
    if (newHeight < 82) {
      newHeight = 82
    }
    height.value = newHeight
  }
  itemContainerHeight.value = unallocatedHolder.value.clientHeight
})

onBeforeUnmount(() => {
  resizeEnd()
})
</script>

<template>
  <div
    ref="resizeableElement"
    class="navbar-light fixed-bottom d-flex border-top flex-column p-0"
    :style="{height: height + 'px'}"
  >
    <droppable-item
      class="flex-grow-1 px-2 overflow-auto"
      :handle-drop="handleUnusedDrop"
      :drop-context="{ 'assignment': null, 'position': null }"
    >
      <section class="mb-1 d-flex">
        <div class="small mt-2 pl-1 text-muted text-unselectable">
          <span
            v-for="(value, key) in sorts"
            :class="['pr-2', value.active ? 'font-weight-bold' : 'hoverable']"
            @click="setSort(key)"
          >{{ gettext(value.label) }}</span>
        </div>
        <div
          class="vc-resize-handler flex-grow-1 mt-2 text-center"
          @dragover.prevent
          @mousedown="resizeStart"
        >
          <i
            data-feather="menu"
            class="mx-auto d-block"
          />
        </div>
        <div class="small text-muted mt-2 mx-1 text-unselectable">
          <span
            :class="['', !showUnavailable ? 'font-weight-bold' : 'hoverable']"
            @click="showUnavailable = false"
          >
            Show Available ({{ filteredAvailable.length }})
          </span>
          <span
            :class="['pl-2', showUnavailable ? 'font-weight-bold' : 'hoverable']"
            @click="showUnavailable = true"
          >
            Show All ({{ filteredAll.length }})
          </span>
        </div>
      </section>
      <section
        ref="unallocatedHolder"
        class="d-flex flex-wrap pb-2"
      >
        <component
          :is="unallocatedComponent"
          v-for="item in currentSortingMethod"
          :key="item.id"
          :item="item"
          :drag-payload="{ 'item': item.id, 'assignment': null, 'position': null }"
        />
      </section>
    </droppable-item>
  </div>
</template>
