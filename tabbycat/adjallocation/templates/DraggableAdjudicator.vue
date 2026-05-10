<script setup>
// Note the checks for "this.adjudicator" are a means of coping when an adj is assigned that is not
// in the master list — i.e. those from another tournament or that were added since the page was loaded
import { computed } from 'vue'
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'
import { useHoverConflictReceiver } from '../../templates/composables/useHoverConflictReceiver.js'
import { useConflictableAdjudicator, useConflictsCSS } from '../../templates/composables/useConflictable.js'

const props = defineProps({
  item: Object,
  dragPayload: Object,
  debateOrPanelId: Number,
  isTrainee: {
    type: Boolean,
    default: false,
  },
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const adjudicator = computed(() => props.item)

const clashableType = computed(() => 'adjudicator')
const clashableID = computed(() => {
  if (props.item && 'id' in props.item) {
    return props.item.id
  }
  return null
})

const highlightData = computed(() => adjudicator.value)
const { highlightsCSS } = useHighlightable({ highlightData })

const hoverReceiver = useHoverConflictReceiver({ clashableType, clashableID })
const hoverConflictsCSS = hoverReceiver.hoverConflictsCSS

const debateOrPanelId = computed(() => props.debateOrPanelId ?? null)
const adjudicatorConflicts = useConflictableAdjudicator({
  debateOrPanelId,
  adjudicator,
  clashableType,
  clashableID,
})

const { conflictsCSS } = useConflictsCSS({
  hasClashConflict: adjudicatorConflicts.hasClashConflict,
  hasInstitutionalConflict: adjudicatorConflicts.hasInstitutionalConflict,
  hasHistoryConflict: adjudicatorConflicts.hasHistoryConflict,
})

const doubleAllocated = computed(() => {
  if (props.item && 'id' in props.item) {
    return store.duplicateAdjudicatorAllocations.includes(props.item.id)
  }
  return false
})

const unavailable = computed(() => {
  if (doubleAllocated.value) {
    return true
  }
  if (props.item && !props.item.available) {
    return true
  }
  return false
})

const hasHistory = computed(() => {
  if (hoverReceiver.hasHoverHistoryConflict.value) {
    return hoverReceiver.hasHoverHistoryConflict.value
  }
  if (adjudicatorConflicts.hasHistoryConflict.value) {
    return adjudicatorConflicts.hasHistoryConflict.value
  }
  return false
})

const maxOccurrences = adjudicatorConflicts.maxOccurrences

const initialledName = computed(() => {
  if (!adjudicator.value) {
    return 'Unknown Adj'
  }
  const names = adjudicator.value.name.split(' ')
  if (names.length > 1) {
    const lastname = names[names.length - 1]
    const lastInitial = lastname[0]
    let firstNames = adjudicator.value.name.split(` ${lastname}`).join('')
    const limit = 10
    if (firstNames.length > limit + 2) {
      firstNames = `${firstNames.substring(0, limit)}…`
    }
    return `${firstNames} ${lastInitial}`
  }
  return names.join(' ')
})

const institutionCode = computed(() => {
  if (adjudicator.value && adjudicator.value.institution) {
    const code = store.institutions?.[adjudicator.value.institution]?.code
    if (!code) {
      return gettext('Unaffiliated')
    }
    const stringDelta = code.length - initialledName.value.length
    if (stringDelta > 3) {
      return code.substring(0, initialledName.value.length + 3) + '…'
    }
    return code
  }
  return gettext('Unaffiliated')
})

const score = computed(() => {
  if (adjudicator.value) {
    return parseFloat(Math.round(adjudicator.value.score * 100) / 100).toFixed(1)
  }
  return 0
})

const scoreA = computed(() => String(score.value)[0])

const scoreB = computed(() => {
  if (!adjudicator.value) {
    return ''
  }
  if (adjudicator.value.score >= 10.0) {
    return String(score.value)[1] + '.'
  }
  return '.' + String(score.value).split('.')[1]
})
</script>

<template>
  <draggable-item
    :drag-payload="dragPayload"
    :hover-panel="true"
    :hover-panel-item="adjudicator"
    :hover-panel-type="'adjudicator'"
    :hover-conflicts="true"
    :hover-conflicts-item="clashableID"
    :hover-conflicts-type="'adjudicator'"
    :class="[{'border-light': isTrainee && conflictsCSS === '', 'bg-dark text-white': unavailable },
             highlightsCSS, conflictsCSS, hoverConflictsCSS]"
  >
    <template #number>
      <span>
        <small class="pl-2 vue-draggable-muted ">{{ scoreA }}{{ scoreB }}</small>
      </span>
    </template>
    <template #title>
      <span>
        {{ initialledName }}
      </span>
    </template>
    <template #subtitle>
      <span>
        {{ institutionCode }}
      </span>
    </template>
    <template #tooltip>
      <div
        v-if="hasHistory"
        class="history-tooltip tooltip"
      >
        <div :class="['tooltip-inner conflictable', 'hover-histories-' + hasHistory + '-ago']">
          {{ hasHistory }} ago <template v-if="maxOccurrences > 1">
            × {{ maxOccurrences }}
          </template>
        </div>
      </div>
    </template>
  </draggable-item>
</template>
