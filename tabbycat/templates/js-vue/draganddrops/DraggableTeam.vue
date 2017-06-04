<template>

  <div draggable=true
       v-bind:class="[componentClasses, isDragging ? vue-is-dragging : '']"
       v-on:dragstart="handleDragStart"
       v-on:dragend="handleDragEnd"
       v-on:mouseenter="showSlideOver(team)"
       v-on:mouseleave="hideSlideOver"><!--
       v-on:mouseenter="show = true"
       v-on:mouseleave="show = false" -->

    <div class="draggable-prefix">
      <h4>{{ team.wins }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ team.short_name }}</h5>
      <span class="small text-muted subtitle">
        {{ team.institution.name }}
      </span>
    </div>

  </div>

</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin],
  props: {
    'team': Object,
    // 'isDragging': { default: false },
  },
  methods: {
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-team', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-team');
    },
  }
}
</script>
