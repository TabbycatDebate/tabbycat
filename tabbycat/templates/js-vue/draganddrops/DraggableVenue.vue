<template>
  <div draggable=true
       :class="[draggableClasses, isDragging ? vue-is-dragging : '']"
       @dragstart="handleDragStart"
       @dragend="handleDragEnd"
       @mouseenter="showSlideOver(venue)"
       @mouseleave="hideSlideOver">

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
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverVenueMixin from '../infoovers/SlideOverVenueMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverVenueMixin],
  props: { 'venue': Object },
  computed: { },
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