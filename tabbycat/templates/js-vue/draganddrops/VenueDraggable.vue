<template>

  <div draggable=true
       v-bind:class="[componentClasses, isDragging ? vue-is-dragging : '']"
       v-on:dragstart="handleDragStart"
       v-on:dragend="handleDragEnd"
       v-on:mouseenter="showSlideOver"
       v-on:mouseleave="hideSlideOver">

    <div class="draggable-prefix">
      <h4>{{ venue.priority }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ venue.name }}</h5>
      <span class="small text-muted subtitle" v-for="c in venue.categories">
        {{ c.name }}
      </span>
      <span class="small text-muted subtitle" v-if="!venue.categories.length">
        N/A
      </span>
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
    showSlideOver: function(event) {
      this.$eventHub.$emit('set-slideover', this.venue)
    },
    hideSlideOver: function(event) {
      this.$eventHub.$emit('unset-slideover')
    },
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-venue', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-venue');
    },
  }
}
</script>
