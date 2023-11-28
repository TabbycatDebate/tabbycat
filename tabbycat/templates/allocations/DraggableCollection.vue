<template>
  <div
    draggable="true"
    @drag="drag"
    @dragstart="dragStartPanel"
    @dragend="dragEndPanel"
    :class="['', draggableClasses]"
  >
    <slot> </slot>
  </div>
</template>

<script>
import DraggableMixin from './DraggableMixin.vue'

export default {
  mixins: [DraggableMixin],
  // Passed down from the parent because the trigger for the show/hide needs to be on this element
  props: {},
  methods: { // Need to track panel drag state globally to mutate UI to hide individual-drop affordances
    dragStartPanel: function (event) {
      this.$store.commit('setPanelDraggingTracker', true)
      this.dragStart(event)
    },
    dragEndPanel: function (event) {
      this.$store.commit('setPanelDraggingTracker', false)
      this.dragEnd(event)
    },
  },
}
</script>
