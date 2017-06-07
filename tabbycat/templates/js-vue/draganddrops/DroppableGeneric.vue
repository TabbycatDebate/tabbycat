<template>

  <div class="vue-droppable"
       ><!--
       @dragover.prevent
       @drop="drop"
       @dragenter="dragEnter"
       @dragleave="dragLeave"
       :class="{ 'vue-is-drag-enter': isDroppable }" -->

    <slot>
      <!-- Container sets the dropped items here -->
    </slot>

  </div>

</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import AjaxMixin from '../draganddrops/AjaxMixin.vue'

export default {
  mixins: [DraggableMixin, AjaxMixin],
  props: { droppable: Object },
  methods: {
    handleDragStart: function(event) {
    },
    handleDragEnd: function(event) {
    },
  }
}
</script>
