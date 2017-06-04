<template>

  <div class="vue-droppable"
       ><!--
       v-on:dragover.prevent
       v-on:drop="drop"
       v-on:dragenter="dragEnter"
       v-on:dragleave="dragLeave"
       v-bind:class="{ 'vue-is-drag-enter': isDroppable }" -->

    <slot>
      <!-- Container sets the dropped items here -->
    </slot>

  </div>

</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import AjaxMixin from '../AjaxMixin.vue'

export default {
  mixins: [DraggableMixin, AjaxMixin],
  props: {
    droppable: Object,
  },
  methods: {
    handleDragStart: function(event) {
    },
    handleDragEnd: function(event) {
    },
  }
}
</script>
