<script setup>
import { computed } from 'vue'
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'
import { useHoverConflictReceiver } from '../../templates/composables/useHoverConflictReceiver.js'

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

const clashableType = computed(() => 'team')
const clashableID = computed(() => props.item?.id ?? null)

const hoverReceiver = useHoverConflictReceiver({ clashableType, clashableID })
const hoverConflictsCSS = hoverReceiver.hoverConflictsCSS

const conflictsCSS = computed(() => {
  const debateId = props.dragPayload?.assignment
  if (!debateId || !props.item) {
    return ''
  }

  const debate = store.allDebatesOrPanels[debateId]
  if (!debate?.teams) {
    return ''
  }

  const otherIds = Object.values(debate.teams).filter(
    teamId => teamId !== null && teamId !== props.item.id,
  )
  if (otherIds.length === 0) {
    return ''
  }

  if (props.item.institution) {
    for (const otherId of otherIds) {
      const otherTeam = store.allocatableItems[otherId]
      if (otherTeam?.institution && otherTeam.institution === props.item.institution) {
        return 'conflictable panel-institution'
      }
    }
  }

  const histories = store.teamHistoriesForItem(props.item.id)
  if (histories?.team) {
    let smallestAgo = 99
    for (const history of histories.team) {
      if (otherIds.includes(history.id) && history.ago < smallestAgo) {
        smallestAgo = history.ago
      }
    }
    if (smallestAgo !== 99) {
      return `conflictable panel-histories-${smallestAgo}-ago`
    }
  }

  return ''
})
</script>

<template>
  <draggable-item
    :drag-payload="dragPayload"
    :class="[{'bg-dark text-white': isUnavailable},
             highlightsCSS, conflictsCSS, hoverConflictsCSS]"
    :hover-panel="true"
    :hover-panel-item="hoverableData"
    :hover-panel-type="hoverableType"
    :hover-conflicts="true"
    :hover-conflicts-item="clashableID"
    :hover-conflicts-type="clashableType"
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
