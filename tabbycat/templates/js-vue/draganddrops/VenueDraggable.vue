<template>

  <div class="vue-draggable btn btn-sm"
    draggable=true
    v-bind:class="[isDragging ? vue-is-dragging : '']"
    v-on:dragstart="handleDragStart"
    v-on:dragend="handleDragEnd"
    :data-id="venue.id"
    v-on:mouseenter="show = true"
    v-on:mouseleave="show = false">
    <span>
      {{ venue.name }}
    </span>
  </div>

</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'

export default {
  mixins: [DraggableMixin],
  props: {
    'venue': Object,
  },
  computed: {

  },
  methods: {
    handleDragStart: function(event) {
      this.$dispatch('started-dragging-venue', this);
    },
    handleDragEnd: function(event) {
      this.$dispatch('stopped-dragging-venue');
    },
  }
}
</script>
