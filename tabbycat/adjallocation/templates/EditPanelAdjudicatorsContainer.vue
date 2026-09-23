<script setup>
import DragAndDropDebate from '../../templates/allocations/DragAndDropDebate.vue'
import DragAndDropLayout from '../../templates/allocations/DragAndDropLayout.vue'
import DragAndDropActions from '../../templates/allocations/DragAndDropActions.vue'
import { useDragAndDropContainer } from '../../templates/composables/useDragAndDropContainer.js'
import { useEditEitherAdjudicators } from '../../templates/composables/useEditEitherAdjudicators.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

import ModalForCreatingPreformedPanels from '../../templates/modals/ModalForCreatingPreformedPanels.vue'
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
  socketBaseLabel: 'panels',
  socketsOverride: ['panels'],
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

const shardIntro = `Sharding narrows the debates displayed to show only a specific subset of the
  overall draw`
const allocateIntro = `Auto-allocate will remove adjudicators from panels and create a new
  allocation in their place.`
const prioritiseIntro = `Using auto-prioritise will remove all existing panel priorities and
  assign new ones.`
const createPanelsInline = `There are no Preformed Panels for this round. You will need to create
  some first by using the button in the top-left.`

const unallocatedComponent = DraggableAdjudicator

const showCreatePanels = () => {
  window.$?.('#confirmCreatePreformedPanelsModal').modal('show')
}

const { allDebatesOrPanels, sortedDebatesOrPanels, debatesOrPanelsCount, unallocatedItems } = container
const { moveAdjudicator, swapPanels, showShard, showAllocate, showPrioritise } = adjudicators
</script>

<template>
  <drag-and-drop-layout
    :unallocated-items="unallocatedItems"
    :unallocated-component="unallocatedComponent"
    :handle-unused-drop="moveAdjudicator"
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
        <template #extra-actions>
          <button
            :class="['btn', debatesOrPanelsCount > 0 ? 'btn-outline-primary' : 'btn-success']"
            @click="showCreatePanels"
          >
            {{ gettext('Create Panels') }}
          </button>
        </template>
        <template #default-highlights>
          <button
            class="btn conflictable conflicts-toolbar hover-histories-2-ago"
            data-toggle="tooltip"
            title="This adjudicator has judged with this adjudicator previously"
          >
            {{ gettext('Seen') }}
          </button>
          <button
            class="btn conflictable conflicts-toolbar hover-institution"
            data-toggle="tooltip"
            title="This adjudicator is from the same institution as this panelist."
          >
            {{ gettext('Institution') }}
          </button>
          <button
            class="btn conflictable conflicts-toolbar hover-adjudicator"
            data-toggle="tooltip"
            title="This adjudicator has a nominated conflict with this panelist."
          >
            {{ gettext('Conflict') }}
          </button>
          <button
            class="btn panel-incomplete"
            data-toggle="tooltip"
            title="Panel is either missing a chair or enough adjudicators for a voting majority."
          >
            {{ gettext('Missing') }}
          </button>
        </template>
      </drag-and-drop-actions>
    </template>

    <template #debates>
      <drag-and-drop-debate
        v-for="panel in sortedDebatesOrPanels"
        :key="panel.pk"
        :debate-or-panel="panel"
      >
        <template #importance>
          <debate-or-panel-importance
            :debate-or-panel="panel"
          />
        </template>
        <template #adjudicators>
          <debate-or-panel-adjudicators
            :debate-or-panel="panel"
            :handle-debate-or-panel-drop="moveAdjudicator"
            :handle-panel-swap="swapPanels"
          />
        </template>
        <template #teams>
          <span />
        </template><!--Hide Teams-->
        <template #venue>
          <span />
        </template><!--Hide Venues-->
      </drag-and-drop-debate>
      <div
        v-if="debatesOrPanelsCount === 0"
        class="text-center lead mx-5 p-5"
      >
        <p class="mx-5 lead mt-2 px-5">
          {{ gettext(createPanelsInline) }}
        </p>
      </div>
    </template>

    <template #modals>
      <modal-for-creating-preformed-panels :context-of-action="'create_preformed_panels'" />
      <modal-for-sharding :intro-text="gettext(shardIntro)" />
      <modal-for-allocating
        :intro-text="gettext(allocateIntro)"
        :for-panels="true"
        :context-of-action="'allocate_panel_adjs'"
      />
      <modal-for-prioritising
        :intro-text="gettext(prioritiseIntro)"
        :context-of-action="'prioritise_panels'"
      />
    </template>
  </drag-and-drop-layout>
</template>
