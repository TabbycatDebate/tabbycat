<template>

  <div draggable=true
       v-bind:class="[componentClasses, isDragging ? vue-is-dragging : '']"
       v-on:dragstart="handleDragStart"
       v-on:dragend="handleDragEnd"><!--
       v-on:mouseenter="show = true"
       v-on:mouseleave="show = false" -->
    <div class="h4 inline-flex">
      {{ venue.name }}
    </div>
  </div>

</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'

export default {
  mixins: [DraggableMixin],
  props: {
    'venue': Object,
    'show': { default: false }
  },
  computed: {

  },
  methods: {
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-venue', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-venue');
    },
  }
}
</script>
