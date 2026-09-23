<script setup>
import { computed } from 'vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHighlightable } from '../../templates/composables/useHighlightable.js'
import { useHoverPanel } from '../../templates/composables/useHoverPanel.js'
import { useHoverConflicts } from '../../templates/composables/useHoverConflicts.js'
import { useHoverConflictReceiver } from '../../templates/composables/useHoverConflictReceiver.js'
import { useConflictableTeam, useConflictsCSS } from '../../templates/composables/useConflictable.js'

const props = defineProps({ team: Object, debateId: Number, isElimination: Boolean })

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()
const { showHoverPanel, hideHoverPanel } = useHoverPanel()
const { showHoverConflicts, hideHoverConflicts } = useHoverConflicts()

const team = computed(() => props.team)
const debateId = computed(() => props.debateId)

const extra = computed(() => store.extra)

const teamName = computed(() => {
  let name = team.value.short_name
  if (extra.value.codeNames === 'everywhere' || extra.value.codeNames === 'admin-tooltips-real') {
    name = team.value.code_name
    if (name === '') {
      name = gettext('No code name set')
    }
  }
  return name
})

const highlightData = computed(() => team.value)
const { highlightsCSS } = useHighlightable({ highlightData })

const clashableType = computed(() => 'team')
const clashableID = computed(() => team.value.id)

const hoverReceiver = useHoverConflictReceiver({ clashableType, clashableID })
const hoverConflictsCSS = hoverReceiver.hoverConflictsCSS

const teamConflicts = useConflictableTeam({
  debateId,
  team,
  clashableType,
  clashableID,
})

const { conflictsCSS } = useConflictsCSS({
  hasClashConflict: teamConflicts.hasClashConflict,
  hasInstitutionalConflict: teamConflicts.hasInstitutionalConflict,
  hasHistoryConflict: teamConflicts.hasHistoryConflict,
})

const hasHistory = computed(() => {
  if (hoverReceiver.hasHoverHistoryConflict.value) {
    return hoverReceiver.hasHoverHistoryConflict.value
  }
  if (teamConflicts.hasHistoryConflict.value) {
    return teamConflicts.hasHistoryConflict.value
  }
  return false
})

const maxOccurrences = teamConflicts.maxOccurrences

const isLive = computed(() => {
  if (props.isElimination || team.value.break_categories.length === 0) {
    return true
  }
  const breakCategoriesCount = team.value.break_categories.length
  let letDeadCategoriesCount = 0
  for (const bc of team.value.break_categories) {
    const category = store.highlights.break.options[bc]
    if (category) {
      if (team.value.points >= category.fields.safe) {
        letDeadCategoriesCount += 1
      }
      if (team.value.points <= category.fields.dead) {
        letDeadCategoriesCount += 1
      }
    }
  }
  return (breakCategoriesCount - letDeadCategoriesCount) > 0
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

const teamAllowedSets = computed(() => {
  try {
    const constraints = extra.value?.constraints
    if (!constraints) { return [] }
    const sets = []
    const teamCats = constraints.teams?.[team.value.id]
    if (teamCats && teamCats.length > 0) { sets.push(teamCats) }
    const instId = team.value.institution
    const instCats = instId ? constraints.institutions?.[instId] : null
    if (instCats && instCats.length > 0) { sets.push(instCats) }
    return sets
  } catch (e) {
    return []
  }
})

const hoveredVenueCategories = computed(() => {
  const cats = store.currentHoverVenueCategories
  if (!cats) { return null }
  return new Set(cats)
})

const venueConstraintOutlineCSS = computed(() => {
  const sets = teamAllowedSets.value
  if (!sets || sets.length === 0) { return '' }

  const isMismatchForCats = (catSet) => {
    if (!catSet) { return false }
    for (const allowed of sets) {
      let intersects = false
      for (const cid of allowed) { if (catSet.has(cid)) { intersects = true; break } }
      if (!intersects) { return true }
    }
    return false
  }

  if (isMismatchForCats(assignedVenueCategoryIds.value)) {
    return 'conflictable panel-adjudicator'
  }
  if (isMismatchForCats(hoveredVenueCategories.value)) {
    return 'conflictable panel-adjudicator'
  }
  return ''
})

const showHovers = () => {
  showHoverPanel(team.value, 'team')
  showHoverConflicts(team.value.id, 'team')
  try {
    const constraints = extra.value?.constraints
    const sets = []
    const teamCats = constraints?.teams?.[team.value.id]
    if (teamCats && teamCats.length > 0) { sets.push(teamCats) }
    const instId = team.value.institution
    const instCats = instId ? constraints?.institutions?.[instId] : null
    if (instCats && instCats.length > 0) { sets.push(instCats) }
    store.setHoverVenueConstraints({ allowedSets: sets, debateId: debateId.value })
  } catch (e) {
    // noop
  }
}

const hideHovers = () => {
  hideHoverPanel()
  hideHoverConflicts()
  store.unsetHoverVenueConstraints()
}
</script>

<template>
  <div
    class="text-truncate small px-1 inline-team flex-fill d-flex align-items-center hover-target"
    :class="[highlightsCSS, conflictsCSS, hoverConflictsCSS, venueConstraintOutlineCSS]"
    @mouseenter="showHovers"
    @mouseleave="hideHovers"
  >
    <div :class="[isLive ? '' : 'not-live']">
      {{ teamName }}
    </div>
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
  </div>
</template>
