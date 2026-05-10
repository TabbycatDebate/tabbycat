<script setup>
import { computed } from 'vue'
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'

const props = defineProps({
  item: Object,
  dragPayload: Object,
  isTrainee: {
    type: Boolean,
    default: false,
  },
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const extra = computed(() => store.extra)

const teamName = computed(() => {
  let name = props.item.short_name
  if (extra.value.codeNames === 'everywhere' || extra.value.codeNames === 'admin-tooltips-real') {
    name = props.item.code_name
    if (name === '') {
      name = gettext('No code name set')
    }
  }
  return name
})

const isUnavailable = computed(() => {
  if (store.round?.stage === 'E') {
    return false
  }
  return !props.item.available
})

const hoverableData = computed(() => props.item)
const hoverableType = computed(() => 'team')

const institutionCode = computed(() => {
  if (props.item.institution) {
    return store.institutions[props.item.institution].code
  }
  return gettext('Unaffiliated')
})

const highlightData = computed(() => props.item)
const { highlightsCSS } = useHighlightable({ highlightData })

const conflictsCSS = computed(() => '')
const hoverConflictsCSS = computed(() => '')
</script>

<template>
  <draggable-item
    :drag-payload="dragPayload"
    :class="[{'bg-dark text-white': isUnavailable},
             highlightsCSS, conflictsCSS, hoverConflictsCSS]"
    :hover-panel="true"
    :hover-panel-item="hoverableData"
    :hover-panel-type="hoverableType"
  >
    <template #number>
      <span class="d-none"><span /></span>
    </template>
    <template #title>
      <span>{{ teamName }}</span>
    </template>
    <template #subtitle>
      <span>{{ institutionCode }}</span>
    </template>
  </draggable-item>
</template>
