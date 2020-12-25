<template>
  <draggable-item :drag-payload="dragPayload"
                  :class="[{ 'bg-dark text-white': !item.available }, highlightsCSS]">

      <span slot="number">
        <small class="pl-2 vue-draggable-muted ">{{ item.priority }}</small>
      </span>
      <span slot="title">
        {{ item.display_name }}
      </span>
      <span slot="subtitle">

      </span>

  </draggable-item>
</template>

<script>
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import HighlightableMixin from '../../templates/allocations/HighlightableMixin.vue'

export default {
  mixins: [HighlightableMixin],
  components: { DraggableItem },
  props: {
    item: Object,
    dragPayload: Object,
    isTrainee: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    highlightData: function () {
      return this.item
    },
  },
}
</script>
