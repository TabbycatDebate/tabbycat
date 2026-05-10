<script setup>
import { computed } from 'vue'
import DragAndDropDebate from '../../templates/allocations/DragAndDropDebate.vue'
import DragAndDropLayout from '../../templates/allocations/DragAndDropLayout.vue'
import DragAndDropActions from '../../templates/allocations/DragAndDropActions.vue'
import { useDragAndDropContainer } from '../../templates/composables/useDragAndDropContainer.js'
import { useEditEitherAdjudicators } from '../../templates/composables/useEditEitherAdjudicators.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

import ModalForSharding from '../../templates/modals/ModalForSharding.vue'
import ModalForPrioritising from '../../templates/modals/ModalForPrioritising.vue'
import ModalForAllocating from '../../templates/modals/ModalForAllocating.vue'

import DebateOrPanelImportance from './DebateOrPanelImportance.vue'
import DebateOrPanelAdjudicators from './DebateOrPanelAdjudicators.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'

const props = defineProps({
  initialData: Object,
})

const { gettext } = useDjangoI18n()

const container = useDragAndDropContainer({
  initialData: props.initialData,
  getUnallocatedItemFromDebateOrPanel: (debateOrPanel) => {
    const itemIDs = []
    for (const positionAdjudicators of Object.entries(debateOrPanel.adjudicators)) {
      positionAdjudicators[1].forEach((adjudicator) => {
        itemIDs.push(Number(adjudicator))
      })
    }
    return itemIDs
  },
})

const adjudicators = useEditEitherAdjudicators({
  allDebatesOrPanels: container.allDebatesOrPanels,
})

const intro = `Sharding narrows the panels displayed to show only a specific subset of all
  panels available.`
const prioritiseIntro = `Using auto-prioritise will remove all existing debate priorities and assign
  new ones.`
const noDebatesInline = 'There are no debates created for this round.'

const unallocatedComponent = DraggableAdjudicator

const maxTeams = computed(() => {
  return Math.max(...container.sortedDebatesOrPanels.value.map(d => d.teams ? d.teams.length : 0), 2)
})

const groupedDebatesByRound = computed(() => {
  const groups = {}
  const roundSlugForWSPath = props.initialData?.round?.seq
  for (const d of container.sortedDebatesOrPanels.value) {
    const seq = d.round_seq ?? roundSlugForWSPath
    if (!Object.prototype.hasOwnProperty.call(groups, seq)) {
      groups[seq] = { round_seq: seq, round_name: d.round_name, debates: [] }
    }
    groups[seq].debates.push(d)
  }
  return Object.values(groups).sort((a, b) => Number(a.round_seq) - Number(b.round_seq))
})

const { allDebatesOrPanels, sortedDebatesOrPanels, debatesOrPanelsCount, unallocatedItems } = container
const { moveAdjudicator, swapPanels, showShard, showAllocate, showPrioritise } = adjudicators
</script>

<template>
  <drag-and-drop-layout
    :unallocated-items="unallocatedItems"
    :unallocated-component="unallocatedComponent"
    :handle-unused-drop="moveAdjudicator"
    :handle-panel-swap="swapPanels"
  >
    <template #actions>
      <drag-and-drop-actions
        :count="debatesOrPanelsCount"
        prioritise="true"
        allocate="true"
        shard="true"
        @show-shard="showShard"
        @show-allocate="showAllocate"
        @show-prioritise="showPrioritise"
      >
        <template #default-highlights>
          <button
            class="btn conflictable conflicts-toolbar hover-histories-2-ago"
            data-toggle="tooltip"
            :title="'Has judged this team or with this adjudicator previously'"
          >
            {{ gettext('Seen') }}
          </button>
          <button
            class="btn conflictable conflicts-toolbar hover-institution"
            data-toggle="tooltip"
            :title="'Is from the same institution as this team or panelist.'"
          >
            {{ gettext('Institution') }}
          </button>
          <button
            class="btn conflictable conflicts-toolbar hover-adjudicator"
            data-toggle="tooltip"
            :title="'Has a nominated conflict with this team or panelist.'"
          >
            {{ gettext('Conflict') }}
          </button>
          <button
            class="btn panel-incomplete"
            data-toggle="tooltip"
            :title="'Panel is missing a chair or enough adjudicators for a voting majority.'"
          >
            {{ gettext('Missing') }}
          </button>
        </template>
      </drag-and-drop-actions>
    </template>

    <template #debates>
      <div
        v-for="(group, gi) in groupedDebatesByRound"
        :key="'r-' + group.round_seq"
        class="mb-4"
      >
        <div
          v-if="groupedDebatesByRound.length > 1"
          class="mt-2 mb-3"
        >
          <hr
            v-if="gi > 0"
            class="my-3"
          >
          <div class="text-muted small">
            {{ group.round_name }}
          </div>
        </div>
        <drag-and-drop-debate
          v-for="debate in group.debates"
          :key="debate.id"
          :debate-or-panel="debate"
          :max-teams="maxTeams"
        >
          <template #importance>
            <debate-or-panel-importance
              :debate-or-panel="debate"
            />
          </template>
          <template #adjudicators>
            <debate-or-panel-adjudicators
              :debate-or-panel="debate"
              :handle-debate-or-panel-drop="moveAdjudicator"
              :handle-panel-swap="swapPanels"
            />
          </template>
          <template #venue>
            <span />
          </template><!--Hide Venues-->
        </drag-and-drop-debate>
      </div>
      <div
        v-if="sortedDebatesOrPanels.length === 0"
        class="text-center lead mx-5 p-5"
      >
        <p class="mx-5 lead mt-2 px-5">
          {{ gettext(noDebatesInline) }}
        </p>
      </div>
    </template>

    <template #modals>
      <modal-for-sharding :intro-text="gettext(intro)" />
      <modal-for-allocating
        :intro-text="
          gettext(`Auto-allocate will remove adjudicators from all debates
        and create new panels in their place.`)
        "
        :context-of-action="'allocate_debate_adjs'"
      />
      <modal-for-prioritising
        :intro-text="gettext(prioritiseIntro)"
        :context-of-action="'prioritise_debates'"
      />
    </template>
  </drag-and-drop-layout>
</template>
