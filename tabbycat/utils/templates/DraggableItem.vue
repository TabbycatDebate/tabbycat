<template>

  <div draggable=true @dragstart="dragStart" @dragend="dragEnd"
       :class="['d-flex m-1 align-items-center align-self-center', dragableClasses]"
       @mouseenter="enableHover ? showHoverPanel(hoverItem, hoverType) : ''"
       @mouseleave="enableHover ? hideHoverPanel() : ''">

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
import HoverableMixin from './HoverableMixin.vue'

export default {
  mixins: [DraggableMixin, HoverableMixin],
  // Passed down from the parent because the trigger for the show/hide needs to be on this element
  props: {
    enableHover: false,
    hoverItem: Object,
    hoverType: String,
  },
}
</script>

<style scoped>
  .vue-draggable {
    position: relative; /* For the position of the tooltip */
  }
  .vue-draggable .history-tooltip {
    bottom: 1px;
    font-size: 12px;
  }
  .vc-title {
    line-height: 0.9;
    font-size: 1.1rem;
  }
  .vc-number {
    letter-spacing: -3px;
  }
  .vc-subtitle {
    font-weight: normal;
    font-size: 0.65rem;
  }
</style>
