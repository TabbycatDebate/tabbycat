<template>

  <div draggable=true @drag="drag" @dragstart="dragStart" @dragend="dragEnd"
       :class="['d-flex m-1 align-items-center align-self-center', dragableClasses]"
       @mouseenter="showHovers" @mouseleave="hideHovers">

    <slot>
      <h4 class="mb-0 py-1 text-monospace vc-draggable-number vc-number">
        <slot name="number"></slot>
      </h4>
      <div class="py-1 pl-2 pr-2 d-flex flex-column flex-truncate">
        <h5 class="mb-0 vc-title text-truncate">
          <slot name="title"></slot>
        </h5>
        <h6 class="mb-0 vue-draggable-muted vc-subtitle text-truncate">
          <slot name="subtitle"></slot>
        </h6>
      </div>
      <slot name="tooltip"></slot>
    </slot>

  </div>

</template>

<script>
import DraggableMixin from './DraggableMixin.vue'
import HoverablePanelMixin from './HoverablePanelMixin.vue'
import HoverableConflictMixin from '../../templates/allocations/HoverableConflictMixin.vue'

export default {
  mixins: [DraggableMixin, HoverablePanelMixin, HoverableConflictMixin],
  // Passed down from the parent because the trigger for the show/hide needs to be on this element
  props: {
    hoverPanel: {
      type: Boolean,
      default: false,
    },
    hoverPanelItem: Object,
    hoverPanelType: String,
    hoverConflicts: {
      type: Boolean,
      default: false,
    },
    hoverConflictsItem: Number,
    hoverConflictsType: String,
  },
  methods: {
    showHovers: function () {
      if (this.hoverPanel) {
        this.showHoverPanel(this.hoverPanelItem, this.hoverPanelType)
      }
      if (this.hoverConflicts) {
        this.showHoverConflicts(this.hoverConflictsItem, this.hoverConflictsType)
      }
    },
    hideHovers: function () {
      if (this.hoverPanel) {
        this.hideHoverPanel()
      }
      if (this.hoverConflicts) {
        this.hideHoverConflicts()
      }
    },
  },
}
</script>
