<template>
  <draggable-collection
    :drag-payload="getPanelDragPayload()"
    class="mx-1 d-flex flex-fill align-items-stretch align-items-center draggable-panel"
  >

    <div :class="['panel-stats small text-monospace text-center', panelIsDragging ? 'd-none' : '']">
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of panel (excluding trainees)')">
        <span v-if="averageScore">{{ averageScore }}</span>
        <span v-else class="text-muted" v-text="gettext('N/A')"></span>
      </div>
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of voting majority in panel')">
        <span v-if="averageVotingScore">{{ averageVotingScore }}</span>
        <span v-else class="text-muted" v-text="gettext('N/A')"></span>
      </div>
    </div>

    <div :class="['align-items-center justify-content-center panel-handle', ]"
         @mouseenter="showPanelHoverConflicts" @mouseleave="hidePanelHoverConflicts">
      <div class="d-flex"><i data-feather="move"></i></div>
    </div>

    <droppable-item
      :class="['p-1 flex-shrink-1 align-items-center justify-content-center panel-pit',
               panelIsDragging ? 'd-flex' : 'd-none']"
      :handle-drop="handlePanelSwap"
      :drop-context="{ assignment: debateOrPanel.id }">
      <div class="px-4 d-flex"><i data-feather="download"></i></div>
    </droppable-item>

    <div class="d-flex vc-chair-flex flex-truncate flex-nowrap">
      <droppable-item
        class="d-flex flex-grow-1"
        :handle-drop="handleDebateOrPanelDrop" :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'C' }">
        <div
          :class="['align-items-center flex-fill', chairID ? 'd-none' : 'd-flex panel-incomplete']"
        >
          <div class="mx-auto py-2 px-3">Ⓒ</div>
        </div>
        <draggable-adjudicator
          v-if="chairID"
          :class="['flex-fill', isHovered ? 'vue-draggable-dragging' : '']"
          :item="allAdjudicators[chairID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(chairID, 'C')"
          style="max-width: 160px">
        </draggable-adjudicator>
      </droppable-item>
    </div>
    <div :class="'d-flex flex-grow-1 border-left'">
      <droppable-item
        :class="[
          'd-flex flex-grow-1 flex-wrap',
          adjudicators.P.length % 2 ? 'panel-incomplete' : '',
        ]"
        :handle-drop="handleDebateOrPanelDrop" :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'P' }"
      >
        <draggable-adjudicator
          :class="[isHovered ? 'vue-draggable-dragging' : '']"
          v-for="adjID in adjudicators.P"
          :item="allAdjudicators[adjID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(adjID, 'P')"
          :key="adjID"
        >
        </draggable-adjudicator>
      </droppable-item>
    </div>
    <div class="d-flex flex-shrink-1 border-left">
      <droppable-item
        class="d-flex flex-grow-1 flex-wrap"
        :handle-drop="handleDebateOrPanelDrop" :locked="panelIsDragging"
        :drop-context="{ assignment: debateOrPanel.id, position: 'T' }"
      >
        <div
          :class="['align-items-center flex-fill', adjudicators.T.length > 0 ? 'd-none' : 'd-flex']"
        >
          <div class="mx-auto py-2 px-4 trainee-indicator">Ⓣ</div>
        </div>
        <draggable-adjudicator
          :class="[isHovered ? 'vue-draggable-dragging' : '']"
          v-for="adjID in adjudicators.T"
          :item="allAdjudicators[adjID]"
          :debate-or-panel-id="debateOrPanel.id"
          :drag-payload="getDragPayload(adjID, 'T')"
          :key="adjID"
          :isTrainee="true"
        >
        </draggable-adjudicator>
      </droppable-item>
    </div>

  </draggable-collection>
</template>

<script>
import DraggableCollection from '../../templates/allocations/DraggableCollection.vue'
import DroppableItem from '../../templates/allocations/DroppableItem.vue'
import DraggableAdjudicator from './DraggableAdjudicator.vue'
import HoverableConflictMixin from '../../templates/allocations/HoverableConflictMixin.vue'
import { mapGetters } from 'vuex'

export default {
  components: { DraggableAdjudicator, DroppableItem, DraggableCollection },
  mixins: [HoverableConflictMixin],
  props: ['debateOrPanel', 'handleDebateOrPanelDrop', 'handlePanelSwap', 'averageScore', 'averageVotingScore'],
  data: function () {
    return {
      isHovered: false, // Used to track and supress hover conflicts in-panel when over the drag handle
    }
  },
  computed: {
    chairID: function () {
      return this.adjudicators.C[0]
    },
    allAdjudicators: function () {
      return this.$store.getters.allocatableItems
    },
    adjudicators: function () {
      return this.debateOrPanel.adjudicators
    },
    ...mapGetters(['panelIsDragging']),
  },
  methods: {
    getDragPayload: function (adjID, position) {
      return {
        item: adjID,
        assignment: this.debateOrPanel.id,
        position: position,
      }
    },
    getPanelDragPayload: function () {
      return {
        panel: this.debateOrPanel.id,
      }
    },
    showPanelHoverConflicts: function () {
      this.$data.isHovered = true
      this.showHoverConflicts(this.debateOrPanel.id, 'panel')
    },
    hidePanelHoverConflicts: function () {
      this.$data.isHovered = false
      this.hideHoverConflicts()
    },
  },
}
</script>
