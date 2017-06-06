<template>
  <div draggable=true
       :class="[componentClasses, isDragging ? vue-is-dragging : '']"
       @dragstart="handleDragStart"
       @dragend="handleDragEnd"
       @mouseenter="showSlideOver(team)"
       @mouseleave="hideSlideOver"><!--
       @mouseenter="show = true"
       @mouseleave="show = false" -->

    <div class="draggable-prefix">
      <h4>{{ team.wins }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ team.short_name }}</h5>
      <span class="small text-muted subtitle">
        {{ team.institution.code }}
      </span>
    </div>

  </div>
</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../infoovers/SlideOverTeamMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverTeamMixin],
  props: { 'team': Object },
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
