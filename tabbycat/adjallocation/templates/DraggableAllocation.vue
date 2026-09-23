<script setup>
import { computed, ref } from 'vue'
import DraggableCollection from '../../templates/allocations/DraggableCollection.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useHoverConflicts } from '../../templates/composables/useHoverConflicts.js'
import { storeToRefs } from 'pinia'

const props = defineProps({
  debateOrPanel: { type: Object, required: true },
  handleDebateOrPanelDrop: { type: Function, required: true },
  handlePanelSwap: { type: Function, required: true },
  averageScore: { type: [String, Number], default: null },
  averageVotingScore: { type: [String, Number], default: null },
})

const store = useDragAndDropStore()
const { allAdjudicators, panelIsDragging } = storeToRefs(store)
const { gettext } = useDjangoI18n()
const { showHoverConflicts, hideHoverConflicts } = useHoverConflicts()

const isHovered = ref(false)

const adjudicators = computed(() => props.debateOrPanel.adjudicators)
const chairID = computed(() => adjudicators.value?.C?.[0] ?? null)

const getDragPayload = (adjID, position) => {
  return { item: adjID, assignment: props.debateOrPanel.id, position: position }
}

const getPanelDragPayload = () => {
  return { panel: props.debateOrPanel.id }
}

const showPanelHoverConflicts = () => {
  isHovered.value = true
  showHoverConflicts(props.debateOrPanel.id, 'panel')
}

const hidePanelHoverConflicts = () => {
  isHovered.value = false
  hideHoverConflicts()
}
</script>

<template>
  <draggable-collection
    :drag-payload="getPanelDragPayload()"
    class="mx-1 d-flex flex-fill align-items-stretch align-items-center draggable-panel"
  >
    <div :class="['panel-stats small text-monospace text-center', panelIsDragging ? 'd-none' : '']">
      <div
        class="py-1"
        data-toggle="tooltip"
        :title="gettext('Average score of panel (excluding trainees)')"
      >
        <span v-if="averageScore">{{ averageScore }}</span>
        <span
          v-else
          class="text-muted"
        >{{ gettext('N/A') }}</span>
      </div>
      <div
        class="py-1"
        data-toggle="tooltip"
        :title="gettext('Average score of voting majority in panel')"
      >
        <span v-if="averageVotingScore">{{ averageVotingScore }}</span>
        <span
          v-else
          class="text-muted"
        >{{ gettext('N/A') }}</span>
      </div>
    </div>

    <div
      class="align-items-center justify-content-center panel-handle"
      @mouseenter="showPanelHoverConflicts"
      @mouseleave="hidePanelHoverConflicts"
    >
      <div class="d-flex">
        <i data-feather="move" />
      </div>
    </div>

    <droppable-item
      :class="['p-1 flex-shrink-1 align-items-center justify-content-center panel-pit',
               panelIsDragging ? 'd-flex' : 'd-none']"
      :handle-drop="handlePanelSwap"
      :drop-context="{ assignment: debateOrPanel.id }"
    >
      <div class="px-4 d-flex">
        <i data-feather="download" />
      </div>
    </droppable-item>

    <div class="d-flex vc-chair-flex flex-truncate flex-nowrap">
      <droppable-item
        class="d-flex flex-grow-1"
        :handle-drop="handleDebateOrPanelDrop"
        :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'C' }"
      >
        <div
          :class="['align-items-center flex-fill', chairID ? 'd-none' : 'd-flex panel-incomplete']"
        >
          <div class="mx-auto py-2 px-3">
            Ⓒ
          </div>
        </div>
        <draggable-adjudicator
          v-if="chairID"
          :class="['flex-fill', isHovered ? 'vue-draggable-dragging' : '']"
          :item="allAdjudicators[chairID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(chairID, 'C')"
          style="max-width: 160px"
        />
      </droppable-item>
    </div>
    <div :class="'d-flex flex-grow-1 border-left'">
      <droppable-item
        :class="[
          'd-flex flex-grow-1 flex-wrap',
          adjudicators.P.length % 2 ? 'panel-incomplete' : '',
        ]"
        :handle-drop="handleDebateOrPanelDrop"
        :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'P' }"
      >
        <draggable-adjudicator
          v-for="adjID in adjudicators.P"
          :key="adjID"
          :class="[isHovered ? 'vue-draggable-dragging' : '']"
          :item="allAdjudicators[adjID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(adjID, 'P')"
        />
      </droppable-item>
    </div>
    <div class="d-flex flex-shrink-1 border-left">
      <droppable-item
        class="d-flex flex-grow-1 flex-wrap"
        :handle-drop="handleDebateOrPanelDrop"
        :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'T' }"
      >
        <div
          :class="['align-items-center flex-fill', adjudicators.T.length > 0 ? 'd-none' : 'd-flex']"
        >
          <div class="mx-auto py-2 px-4 trainee-indicator">
            Ⓣ
          </div>
        </div>
        <draggable-adjudicator
          v-for="adjID in adjudicators.T"
          :key="adjID"
          :class="[isHovered ? 'vue-draggable-dragging' : '']"
          :item="allAdjudicators[adjID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(adjID, 'T')"
          :is-trainee="true"
        />
      </droppable-item>
    </div>
  </draggable-collection>
</template>
