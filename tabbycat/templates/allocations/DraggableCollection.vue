<template>
  <div
    draggable="true"
    @drag="drag"
    @dragstart="dragStart"
    @dragend="dragEnd"
    :class="['', dragableClasses]"
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
  methods: {},
}
</script>
