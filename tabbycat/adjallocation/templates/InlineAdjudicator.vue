<script setup>
import { computed } from 'vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'
import { useHoverConflictReceiver } from '../../templates/composables/useHoverConflictReceiver.js'
import { useConflictableAdjudicator, useConflictsCSS } from '../../templates/composables/useConflictable.js'

defineOptions({ name: 'InlineAdjudicator' })

const props = defineProps({
  adjudicator: { type: Object, required: true },
  debateId: { type: Number, required: true },
  role: { type: String, default: 'P' }, // C, P, T
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const adjudicator = computed(() => props.adjudicator)
const debateId = computed(() => props.debateId)

const extra = computed(() => store.extra)

const displayName = computed(() => adjudicator.value?.name || gettext('Unknown Adj'))

const symbol = computed(() => {
  if (props.role === 'C') return 'Ⓒ'
  if (props.role === 'T') return 'Ⓣ'
  return ''
})

const highlightData = computed(() => adjudicator.value)
const { highlightsCSS } = useHighlightable({ highlightData })

const clashableType = computed(() => 'adjudicator')
const clashableID = computed(() => adjudicator.value?.id ?? null)

const hoverReceiver = useHoverConflictReceiver({ clashableType, clashableID })
const hoverConflictsCSS = hoverReceiver.hoverConflictsCSS

const adjConflicts = useConflictableAdjudicator({
  debateOrPanelId: debateId,
  adjudicator,
  clashableType,
  clashableID,
})

const { conflictsCSS } = useConflictsCSS({
  hasClashConflict: adjConflicts.hasClashConflict,
  hasInstitutionalConflict: adjConflicts.hasInstitutionalConflict,
  hasHistoryConflict: adjConflicts.hasHistoryConflict,
})

const assignedVenueCategoryIds = computed(() => {
  try {
    const debate = store.debatesOrPanels?.[debateId.value]
    if (!debate || !debate.venue) { return null }
    let venueObj = debate.venue
    if (typeof venueObj === 'number') {
      venueObj = store.allocatableItems?.[venueObj]
    }
    const cats = venueObj?.categories ?? null
    if (!cats) { return null }
    return new Set(cats.map(c => (typeof c === 'object' ? c.id : c)))
  } catch (e) {
    return null
  }
})

const adjudicatorAllowedSets = computed(() => {
  try {
    const constraints = extra.value?.constraints
    if (!constraints) { return [] }
    const sets = []
    const adjCats = constraints.adjudicators?.[adjudicator.value.id]
    if (adjCats && adjCats.length > 0) sets.push(adjCats)
    const instId = adjudicator.value.institution
    const instCats = instId ? constraints.institutions?.[instId] : null
    if (instCats && instCats.length > 0) sets.push(instCats)
    return sets
  } catch (e) {
    return []
  }
})

const hoveredVenueCategories = computed(() => {
  const cats = store.currentHoverVenueCategories
  if (!cats) return null
  return new Set(cats)
})

const venueConstraintOutlineCSS = computed(() => {
  const sets = adjudicatorAllowedSets.value
  if (!sets || sets.length === 0) return ''

  const isMismatchForCats = (catSet) => {
    if (!catSet) return false
    for (const allowed of sets) {
      let intersects = false
      for (const cid of allowed) { if (catSet.has(cid)) { intersects = true; break } }
      if (!intersects) return true
    }
    return false
  }

  if (isMismatchForCats(assignedVenueCategoryIds.value)) return 'conflictable panel-adjudicator'
  if (isMismatchForCats(hoveredVenueCategories.value)) return 'conflictable panel-adjudicator'
  return ''
})

const showHovers = () => {
  try {
    const sets = []
    const constraints = store.extra?.constraints
    const adjCats = constraints?.adjudicators?.[adjudicator.value.id]
    if (adjCats && adjCats.length > 0) sets.push(adjCats)
    const instId = adjudicator.value.institution
    const instCats = instId ? constraints?.institutions?.[instId] : null
    if (instCats && instCats.length > 0) sets.push(instCats)
    store.setHoverVenueConstraints({ allowedSets: sets, debateId: debateId.value })
  } catch (e) {
    // noop
  }
}

</script>

<template>
  <div
    class="text-truncate small px-1 py-1 inline-adjudicator d-flex align-items-center hover-target"
    :class="[highlightsCSS, conflictsCSS, hoverConflictsCSS, venueConstraintOutlineCSS]"
    @mouseenter="showHovers"
    @mouseleave="store.unsetHoverVenueConstraints"
  >
    <div>{{ displayName }}<span v-if="symbol">&nbsp;{{ symbol }}</span></div>
  </div>
</template>
