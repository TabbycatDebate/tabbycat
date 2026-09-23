<script setup>
import { computed, ref } from 'vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'

const props = defineProps({ debateOrPanel: Object })

const store = useDragAndDropStore()
const showTooltip = ref(false)

const importance = computed({
  get () {
    return parseInt(props.debateOrPanel.importance)
  },
  set (value) {
    const importanceChanges = [{ id: props.debateOrPanel.id, importance: value }]
    store.updateDebatesOrPanelsAttribute({ importance: importanceChanges })
  },
})

const importanceDescription = computed(() => {
  if (importance.value === 2) {
    return 'V.I.P. Priority'
  } else if (importance.value === 1) {
    return 'Important Priority'
  } else if (importance.value === 0) {
    return 'Neutral Priority'
  } else if (importance.value === -1) {
    return 'Unimportant Priority'
  } else if (importance.value === -2) {
    return '¯\\_(ツ)_/¯ Priority'
  }
  return null
})
</script>

<template>
  <div
    class="flex-4 flex-truncate d-flex border-right align-items-center"
    @mouseover="showTooltip=true"
    @mouseleave="showTooltip=false"
  >
    <input
      v-model="importance"
      max="2"
      min="-2"
      step="1"
      type="range"
    >

    <div
      v-if="showTooltip"
      class="tooltip top tooltip-vue mt-5 ml-3"
      role="tooltip"
    >
      <div class="tooltip-arrow" />
      <div class="tooltip-inner">
        {{ importanceDescription }}
      </div>
    </div>
  </div>
</template>
